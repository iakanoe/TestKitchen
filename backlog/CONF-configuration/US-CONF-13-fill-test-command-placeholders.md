---
id: US-CONF-13
type: story
title: Fill the test command placeholders
epic: EP-CONF
source_reqs: [CONF-R19]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project maintainer, I want `test_command` placeholders filled safely, so that any test runner, including one started inside a subfolder, runs exactly the selected files and writes its report where Test Kitchen reads it.

## Acceptance criteria

- AC1: Given a command with `{files}` and a list of test files, when it is rendered, then `{files}` becomes the files, root-relative, each shell-quoted, separated by spaces.
- AC2: Given a command with `{files}` and no files (a full run), when it is rendered, then `{files}` becomes empty.
- AC3: Given a command with `{files:<dir>}`, when it is rendered, then each file is written relative to `<dir>`, slashes around `<dir>` are ignored, and an empty `<dir>` behaves like `{files}`.
- AC4: Given a command with `{files:<dir>}` and a file outside `<dir>`, when it is rendered, then that file is reached with `../`.
- AC5: Given a command with `{report}`, when it is rendered, then it becomes the report path, shell-quoted.
- AC6: Given a command with other brace text, such as a shell variable or a brace list, when it is rendered, then that text is left unchanged.

## Notes

`guide/configuration.md` describes `{files:<dir>}` as removing the `<dir>/` prefix; the code computes a relative path, which is the same for files inside `<dir>`. Which files are selected, and requiring `{report}`, belong to the delivery epic.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
