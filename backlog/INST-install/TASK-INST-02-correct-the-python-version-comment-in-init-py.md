---
id: TASK-INST-02
type: task
title: Correct the Python version comment in init.py
epic: EP-INST
source_reqs: [INST-R32]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: draft
---

The comment at `init.py`'s Python version check says the check exists so an old interpreter gets a sentence, not a traceback. On Python 3.6 and older the file fails to compile before the check runs, so the comment overstates what the check does. This task corrects the comment; the behavior stays as it is.

## Acceptance criteria

- AC1: The comment at the version check in `init.py` says that Python 3.7 and later get the version sentence.
- AC2: No behavior changes: Python 3.7 and 3.8 still stop with the sentence and exit 1 (INST-R03), and only the comment differs in the diff.

## Notes

Implements DEC-INST-02, option (b), decided 2026-11-25 by Ianick Noejovich: Python 3.6 and older getting a syntax error is accepted. US-INST-02 records the prerequisite checks and stays as it is.

## Open questions

- None.
