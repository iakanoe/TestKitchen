"""A fake test runner for the tests: writes a JUnit XML report from plain-text "test files".

Used as `test_command: <python> <this file> {report} {files}` so `deliver.py gate red` and
`check` can be tested without any real test framework. Each test file line of exactly two
words, `<test name> pass|fail|skip`, is one test case; every other line is ignored (so the
same files can hold tag text for `gate pr`). An optional third word sets the case's
classname (default: the file's path), so tags in class names can be tested.

Behaviors a test can ask for through the environment:
    JUNIT_RUNNER_NO_REPORT=1   exit 3 without writing a report (the tests "could not run")
    JUNIT_RUNNER_BAD_XML=1     write a report that is not XML

Exit code: 1 when any case failed, else 0, as test runners do.
"""
import os
import sys
from xml.sax.saxutils import quoteattr


def main():
    report, files = sys.argv[1], sys.argv[2:]
    print("runner got files:", " ".join(files))
    if os.environ.get("JUNIT_RUNNER_NO_REPORT"):
        print("cannot start: the test framework is missing", file=sys.stderr)
        return 3
    cases, failed = [], False
    for path in files:
        with open(path, encoding="utf-8") as f:
            for line in f:
                words = line.split()
                if len(words) not in (2, 3) or words[1] not in ("pass", "fail", "skip"):
                    continue
                classname = words[2] if len(words) == 3 else path
                inner = {"fail": "<failure message='expected'/>", "skip": "<skipped/>", "pass": ""}[words[1]]
                failed = failed or words[1] == "fail"
                cases.append(f"<testcase classname={quoteattr(classname)} name={quoteattr(words[0])}>{inner}</testcase>")
    with open(report, "w", encoding="utf-8") as f:
        if os.environ.get("JUNIT_RUNNER_BAD_XML"):
            f.write("<testsuite><testcase")
        else:
            f.write(f"<testsuites><testsuite name='fixture'>{''.join(cases)}</testsuite></testsuites>")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
