#!/usr/bin/env python3
"""Convert xcresult JSON to JUnit XML. Fallback: parse xcodebuild raw output."""
import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape, quoteattr


def parse_xcresult(data):
    """Extract test results and failure summaries from xcresult JSON."""
    gv = lambda obj: obj['_value'] if isinstance(obj, dict) and '_value' in obj else ''

    # Failure summaries
    failures = {}
    try:
        for action in data.get('actions', {}).get('_values', []):
            for f in action.get('actionResult', {}).get('issues', {}).get('testFailureSummaries', {}).get('_values', []):
                name = gv(f.get('testCaseName', {}))
                msg = gv(f.get('message', {}))
                url = gv(f.get('documentLocationInCreatingWorkspace', {}).get('url', {}))
                if name and msg:
                    loc = re.search(r'file://([^#]+)#.*?StartingLineNumber=(\d+)', url)
                    failures[name] = msg + (f"\n\n  at {loc.group(1)}: line {loc.group(2)}" if loc else '')
    except (KeyError, TypeError):
        pass

    # Walk for test metadata
    tests = []

    def walk(obj):
        if isinstance(obj, dict):
            t = obj.get('_type', {})
            if isinstance(t, dict) and t.get('_value') == 'ActionTestMetadata':
                name = gv(obj.get('name', {}))
                if name:
                    status = gv(obj.get('testStatus', {}))
                    tests.append({
                        'name': name,
                        'duration': float(gv(obj.get('duration', {})) or 0),
                        'passed': status == 'succeeded',
                        'failure_output': failures.get(name, ''),
                    })
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    return tests, failures


def parse_xcodebuild_log(log_path):
    """Parse raw xcodebuild output for test results and failure output."""
    with open(log_path, encoding='utf-8', errors='replace') as f:
        log = f.read()

    tests = []
    pattern = r"Test case '(\S+\.\S+)' (passed|failed) on '[^']+' \((\d+\.?\d*) seconds\)"
    matches = list(re.finditer(pattern, log))

    for i, m in enumerate(matches):
        name, status, duration = m.groups()
        failure_output = ''
        if status == 'failed':
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(log)
            chunk = log[start:end]
            lines = [
                line.strip() for line in chunk.split('\n')
                if line.strip() and (
                    ': error:' in line or ': warning:' in line or
                    'XCTAssert' in line or 'failed' in line.lower() or
                    line.strip().endswith('.swift')
                )
            ]
            failure_output = '\n'.join(lines) if lines else chunk.strip()[:2000]

        tests.append({
            'name': name,
            'duration': float(duration),
            'passed': status == 'passed',
            'failure_output': failure_output,
        })
    return tests


def extract_test_output_section(log_path):
    """Extract the test execution section from xcodebuild output for system-err."""
    try:
        with open(log_path, encoding='utf-8', errors='replace') as f:
            log = f.read()
        # Try markers in order of specificity
        for start_pat in [r"Test suite '\S+' started", r"Testing started", r"Test Case "]:
            m = re.search(start_pat, log)
            if m:
                start = m.start()
                end_m = re.search(r'\*\* TEST (?:SUCCEEDED|FAILED) \*\*|Test session results', log[start:])
                section = log[start:start + end_m.start() if end_m else len(log)]
                return section.strip()
    except (FileNotFoundError, OSError):
        pass
    return ''


def cdata(text):
    """Wrap text in CDATA, escaping any nested ]]>."""
    return '<![CDATA[' + text.replace(']]>', ']]]]><![CDATA[>') + ']]>'


def to_junit_xml(tests, output_path, test_output=''):
    """Write tests to JUnit XML format (Gradle-compatible). Groups by classname."""
    failures = sum(1 for t in tests if not t['passed'])
    total_time = round(sum(t['duration'] for t in tests), 3)
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    hostname = escape(socket.gethostname())

    # Derive suite name from test classnames
    classnames = sorted({t['name'].split('.')[0] for t in tests}) if tests else ['test1Tests']
    suite_name = classnames[0] if len(classnames) == 1 else 'test1'

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<testsuite name="{suite_name}" tests="{len(tests)}" skipped="0" failures="{failures}"'
        f' errors="0" timestamp="{timestamp}" hostname="{hostname}" time="{total_time}">',
        '  <properties/>',
    ]

    for t in tests:
        classname = t['name'].split('.')[0] if '.' in t['name'] else suite_name
        method = t['name'].split('.', 1)[-1].rstrip('()')
        line = f'  <testcase name={quoteattr(method)} classname={quoteattr(classname)} time="{t["duration"]:.3f}"'
        if t['passed']:
            lines.append(line + '/>')
        else:
            msg = (t.get('failure_output') or 'Test failed').strip()[:5000]
            lines.append(line + '>')
            lines.append(f'    <failure message={quoteattr(msg[:500])}>{escape(msg)}</failure>')
            lines.append('  </testcase>')

    lines.append(f'  <system-out>{cdata("")}</system-out>')
    err_content = test_output if test_output and failures > 0 else ''
    lines.append(f'  <system-err>{cdata(err_content)}</system-err>')
    lines.append('</testsuite>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else 'test-report.xml'

    # Try xcresult JSON first
    tests, failure_summaries = [], {}
    try:
        result = subprocess.run(
            ['xcrun', 'xcresulttool', 'get', '--path', 'TestResults.xcresult', '--format', 'json', '--legacy'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout:
            tests, failure_summaries = parse_xcresult(json.loads(result.stdout))
    except Exception:
        pass

    log_path = 'raw-test.log' if os.path.exists('raw-test.log') else '/tmp/xcode-test-output.log'

    # Fallback to raw log parsing
    if not tests:
        try:
            tests = parse_xcodebuild_log(log_path)
        except FileNotFoundError:
            print('No test results found. Run xcodebuild test first.', file=sys.stderr)
            sys.exit(1)

    # Merge richer xcresult failure summaries into tests; fall back to log for missing ones
    for t in tests:
        if not t['passed']:
            if t['name'] in failure_summaries:
                t['failure_output'] = failure_summaries[t['name']]
    if any(not t['passed'] and not t['failure_output'] for t in tests):
        try:
            log_by_name = {lt['name']: lt for lt in parse_xcodebuild_log(log_path)}
            for t in tests:
                if not t['passed'] and not t['failure_output'] and t['name'] in log_by_name:
                    t['failure_output'] = log_by_name[t['name']].get('failure_output', '')
        except (FileNotFoundError, OSError):
            pass

    to_junit_xml(tests, output_path, extract_test_output_section(log_path))
    print(f"Wrote JUnit XML to {output_path} ({len(tests)} tests)")


if __name__ == '__main__':
    main()
