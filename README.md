# iOS/macOS Test Importer

iOS/macOS Swift app with unit tests, JUnit XML output, and Gradle/Develocity integration.

## Quick start

```bash
./run_tests_xml.sh
```

Runs **unit tests only** (not UI tests), generates `test-report.xml`, and executes the Gradle `import` task (which sends results to Develocity).

## Project structure

- **test1/** – Main app (SwiftUI)
- **test1Tests/** – Unit tests
- **test1UITests/** – UI tests (run in CI only)
- **run_tests_xml.sh** – Runs tests and produces JUnit XML
- **build.gradle.kts** – Gradle config; `import` task imports `test-report.xml` into Develocity

## Requirements

- Xcode
- Python 3
- Java 17+

## CI

GitHub Actions runs **unit tests** (macOS) and **UI tests** (iOS Simulator) in separate jobs on push/PR to `main`, then imports the JUnit XML reports to Develocity.

## Example
* https://ge.solutions-team.gradle.com/s/2vhv6xhxei43m
* https://ge.solutions-team.gradle.com/s/emkn6aqt63gsw
