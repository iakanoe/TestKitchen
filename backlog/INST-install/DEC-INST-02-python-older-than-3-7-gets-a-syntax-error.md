---
id: DEC-INST-02
type: decision
title: Python older than 3.7 gets a syntax error instead of the version message
epic: EP-INST
source_reqs: [INST-R03]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Question

Is this intended? On Python 3.6 or older, `init.py` fails with a syntax error before its "Test Kitchen needs Python 3.9 or later" check can run.

## Context

- Current behavior: `init.py:33` is `from __future__ import annotations`, a feature that exists from Python 3.7. A `__future__` import the interpreter does not know is a compile-time error, so the whole file fails to compile and the version check at `init.py:37-44` never runs. Python 2 fails earlier still, on the annotated function signatures.
- Evidence: the standard library's own record, `python3 -c "import __future__; print(__future__.annotations)"`, gives `_Feature((3, 7, 0, 'beta', 1), …)`, the release that introduced it. Not run on a real Python 3.6, which is not installed here.
- The comment at `init.py:37-38` says the check exists "so an old interpreter gets a sentence, not a traceback"; that holds for 3.7 and 3.8 only.
- Already settled: Python 3.9 is the supported minimum (decision log, "CI runs Python 3.9 on Ubuntu 24.04"; `docs/spec-v0.1.md` section 0). The spec does not say which older interpreters must get the friendly message.
- Likely intended: any `python3` too old to run the file gets the sentence. Which old versions still matter in practice (3.6 shipped with some long-term-support Linux releases) is not recorded.

## Options

None recorded. Proposals, not decisions:

- (a) Drop `from __future__ import annotations` from `init.py` and keep annotations that 3.6 can parse (or move them to string form), so the check runs on 3.6 too.
- (b) Accept it: 3.6 is end-of-life, and correct the comment to say 3.7 and later get the sentence.

## Recommendation

(b) unless the person knows of users on Python 3.6: the cost of (a) is a style exception in one file for interpreters that are long out of support.

## Decides

No ticket waits on it. US-INST-02/AC1 records today's behavior for 3.7 and 3.8; a change becomes a new story or task under EP-INST.
