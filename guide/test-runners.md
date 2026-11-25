# Test runners

Test Kitchen reads test results in one format, JUnit XML, and finds which criterion a test proves from a tag in the test's name. Any runner works if its `test_command` writes JUnit XML to `{report}` and the tag reaches the XML.

## How results are read

`deliver.py gate red` runs `test_command` with `{files}` set to the ticket's tagged test files and `{report}` set to a temporary file, then reads every `<testcase>`: its `name` and `classname` are searched for tags; a `<failure>` or `<error>` child means it failed, a `<skipped>` child that it was skipped. If no report was written, the gate fails and shows the end of the command's output.

## Tag forms

- canonical: `[US-PAY-03/AC2]` anywhere in the test name, or in a describe or class name;
- identifier: `us_pay_03_ac2` in any case, bounded by characters that are not letters or digits: `test_us_pay_03_ac2_refund_denied`, `TestUS_PAY_03_AC2`.

Use the canonical form where test names are free text (JavaScript, subtests) and the identifier form where they are identifiers (Python functions, Java methods). In every runner, the safest place is the test's own name.

To see what your runner reports, run the command once by hand with a report path and read the XML:

```sh
python3 -m pytest tests/test_refund.py --junitxml=/tmp/report.xml; grep '<testcase' /tmp/report.xml
```

## pytest

```yaml
test_command: "python3 -m pytest {files} --junitxml={report}"
```

`name` is the test function (with any parametrize id), `classname` the module path plus the class. Tag with the identifier form:

```python
def test_us_pay_03_ac2_refund_over_total_is_refused():
    ...

class TestUS_PAY_03_AC1:
    def test_refund_equal_to_total_is_accepted(self):
        ...
```

Import the module, not the names it doesn't have yet. `from payments import refund` fails while the module is collected, before any test runs, so pytest reports one collection error with no tags and `gate red` says "no tagged test ran". `import payments` and calling `payments.refund(…)` makes each test fail on its own, with its tag. For a module that doesn't exist yet, import it inside each test. Don't add stub code to get past the import: code changed before the freeze commit fails `gate pr`.

## Vitest

```yaml
test_command: "npx vitest run {files} --reporter=default --reporter=junit --outputFile.junit={report}"
```

Two reporters: `default` prints to the console, `junit` writes `{report}`. `name` holds the describe titles and the test title joined by ` > `; `classname` is the file path. Tag the test or its describe:

```ts
describe("[US-PAY-03/AC2] refund over the total", () => {
  it("is refused", () => { /* … */ });
});
```

## Jest

```yaml
test_command: "JEST_JUNIT_OUTPUT_FILE={report} npx jest --ci --reporters=default --reporters=jest-junit {files}"
```

Needs the `jest-junit` package (`npm install --save-dev jest-junit`), which reads the output path from `JEST_JUNIT_OUTPUT_FILE`. By default both `name` and `classname` hold the describe names and the test title, so the tag can go in either.

## Node's built-in runner (node:test)

```yaml
test_command: "node --test --test-reporter=spec --test-reporter-destination=stdout --test-reporter=junit --test-reporter-destination={report} {files}"
```

Reporters and destinations pair up in order: `spec` to the console, `junit` to `{report}`. Your Node version must ship the `junit` reporter; with no files given, `node --test` finds the test files itself. `name` is the test's title, and `classname` the innermost `describe` title (`test` at the top level), so put the tag in the test title or the innermost describe:

```js
import { it } from "node:test";
it("[US-PAY-03/AC2] refuses a refund over the total", () => { /* … */ });
```

## Go

```yaml
test_command: "gotestsum --junitfile {report} -- ./..."
```

`go test` does not write JUnit XML; [gotestsum](https://github.com/gotestyourself/gotestsum) runs it and does (`go install gotest.tools/gotestsum@latest`). `go test` takes packages, not files, so this command leaves out `{files}` and always runs the whole suite; tags still pick each criterion's tests out by name. `classname` is the package path. Tag the function name or a subtest name (Go turns spaces in subtest names into underscores and keeps the brackets):

```go
func TestUS_PAY_03_AC2_RefundOverTotal(t *testing.T) { /* … */ }

func TestRefund(t *testing.T) {
    t.Run("[US-PAY-03/AC2] over the total is refused", func(t *testing.T) { /* … */ })
}
```

## JUnit 5 (Gradle or Maven)

Gradle and Maven Surefire write one XML file per test class (`build/test-results/test/TEST-*.xml`, `target/surefire-reports/TEST-*.xml`), and `{report}` is one file. Keep a small merge script in your project, for example `tools/merge_junit.py`:

```python
"""Merges JUnit XML files into one: merge_junit.py OUT IN [IN ...]."""
import sys
import xml.etree.ElementTree as ET

merged = ET.Element("testsuites")
for path in sys.argv[2:]:
    root = ET.parse(path).getroot()
    merged.extend([root] if root.tag == "testsuite" else list(root))
ET.ElementTree(merged).write(sys.argv[1], encoding="utf-8", xml_declaration=True)
```

```yaml
# Gradle
test_command: "./gradlew cleanTest test --continue; s=$?; python3 tools/merge_junit.py {report} build/test-results/test/TEST-*.xml; exit $s"
# Maven
test_command: "mvn -q clean test; s=$?; python3 tools/merge_junit.py {report} target/surefire-reports/TEST-*.xml; exit $s"
```

Both run the whole suite (their test filters take class names, not paths) and clean first so no stale result files are read. `name` is the method name and `classname` the class, so tag with the identifier form in the method name; display names do not always reach the XML.

```java
@Test
void us_pay_03_ac2_refundOverTotalIsRefused() { /* … */ }
```

## Skipped and focused tests

After the freeze, `gate pr` refuses any added skipped or focused test, because a skipped test proves nothing and a focused one silently drops the rest. The built-in detector covers at least:

| Language | Patterns |
| --- | --- |
| JavaScript, TypeScript | `.skip(`, `.only(`, `.todo(`, `.fixme(`, `xit(`, `xdescribe(`, `xtest(`, `fit(`, `fdescribe(` |
| Python | `@pytest.mark.skip`, `@pytest.mark.skipif`, `@pytest.mark.xfail`, `pytest.skip(`, `@unittest.skip`, `self.skipTest(` |
| Go | `t.Skip(` |
| JVM | `@Disabled`, `@Ignore` |
| Ruby | `skip`, `xit`, `pending` |
