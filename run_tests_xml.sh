#!/bin/bash
# Run Xcode unit tests, output JUnit XML, then optionally run a Gradle task
# Usage: ./run_tests_xml.sh [output_file]
#        GRADLE_PROJECT=../my-gradle-project GRADLE_TASK=build ./run_tests_xml.sh
#
# Env vars (optional):
#   GRADLE_PROJECT - path to Gradle project (relative to script dir or absolute)
#   GRADLE_TASK    - Gradle task to run after tests (default: build)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
OUTPUT="${1:-test-report.xml}"

# Remove existing result bundle so xcodebuild doesn't fail
rm -rf ./TestResults.xcresult

echo "Running unit tests..."
xcodebuild test \
  -scheme test1 \
  -destination 'platform=macOS,arch=arm64' \
  -only-testing:test1Tests \
  -resultBundlePath ./TestResults.xcresult \
  2>&1 | tee /tmp/xcode-test-output.log | tee "$SCRIPT_DIR/raw-test.log"

echo "Generating JUnit XML..."
python3 "$SCRIPT_DIR/xcresult_to_junit.py" "$OUTPUT"

echo "Done. Report: $OUTPUT"

# Run Gradle task if configured (default: same folder, import task)
if [ -n "${GRADLE_PROJECT}" ] || [ -f "$SCRIPT_DIR/build.gradle.kts" ]; then
  GRADLE_DIR="${GRADLE_PROJECT:-.}"
  [ "${GRADLE_DIR:0:1}" != "/" ] && GRADLE_DIR="$SCRIPT_DIR/$GRADLE_DIR"
  GRADLE_TASK="${GRADLE_TASK:-import}"
  if [ -f "$GRADLE_DIR/build.gradle" ] || [ -f "$GRADLE_DIR/build.gradle.kts" ]; then
    echo "Running Gradle task: $GRADLE_TASK in $GRADLE_DIR"
    (cd "$GRADLE_DIR" && if [ -x ./gradlew ]; then ./gradlew $GRADLE_TASK; else gradle $GRADLE_TASK; fi)
  else
    echo "Warning: No Gradle project found at $GRADLE_DIR"
    exit 1
  fi
fi
