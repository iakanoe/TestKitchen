---
id: TASK-INST-02
type: task
title: Correct the Python version comment in init.py
epic: EP-INST
source_reqs: [INST-R32]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: in-progress
refined: 2026-11-26
---

The comment at `init.py`'s Python version check says the check exists so an old interpreter gets a sentence, not a traceback. On Python 3.6 and older the file fails to compile before the check runs, so the comment overstates what the check does. This task corrects the comment; the behavior stays as it is.

## Acceptance criteria

- AC1: The comment at the version check in `init.py` says that Python 3.7 and later get the version sentence.
- AC2: Only that comment differs in `init.py`; the version check itself is unchanged.

## Notes

- Implements DEC-INST-02, option (b), decided 2026-11-25 by Ianick Noejovich: Python 3.6 and older getting a syntax error is accepted.
- US-INST-02/AC1 keeps Python 3.7 and 3.8 stopping with the sentence and exit 1 (INST-R03); US-INST-02 stays as it is.
- The final review verifies both criteria by reading the diff.

## Open questions

- None. The decision log records this decision.
