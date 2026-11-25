---
id: DEC-INST-04
type: decision
title: A malformed lock version ends update in a traceback
epic: EP-INST
source_reqs: [INST-R27, INST-R17]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? When `kitchen.lock` holds a `version` that is not a dotted number (for example `"main"` after a hand edit or a botched conflict resolution), `init.py update` ends in a Python traceback instead of an `error:` line.

## Context

- Current behavior: `update` reads `lock["version"]` as text (`init.py:1105`) and compares it with `vtuple` (`init.py:175-176`, called at `init.py:1163` and inside `migration_notes`), which raises `ValueError` on any part that is not a number. `main` catches only `UsageError`, `Failure`, and `KeyboardInterrupt` (`init.py:1533-1541`), so the exception reaches the interpreter.
- Reproduced on 2026-11-25 in a throwaway repository: after setting the lock's `version` to `"main"`, `update --yes` printed a traceback ending in `ValueError: invalid literal for int() with base 10: 'main'` and exited 1. Nothing was written, because the comparison happens before the confirmation.
- The same code turns other lock problems into clear messages: a lock that is not JSON or has no `files` table gives `error: kitchen.lock … Restore it from git history.` (`init.py:868-873`). The lock's `about` field says not to edit it.
- Likely intended: the same kind of message for a bad `version` (exit 1, restore the lock from git history).

## Options

None recorded. Proposals, not decisions:

- (a) Validate the lock's `version` in `read_lock` and raise the same "Restore it from git history" failure.
- (b) Accept it: the lock is not meant to be edited by hand.

## Recommendation

(a): one check, and every lock problem then reads the same way.

## Decides

No ticket waits on it. US-INST-22 records today's behavior; a fix becomes a new story under EP-INST.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): a `kitchen.lock` whose `version` is not a dotted number gives the same `error: kitchen.lock … Restore it from git history.` failure (exit 1) as other broken locks.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R34; superseded INST-R27 (by INST-R34); confirmed INST-R17; US-INST-27; decision log, "A lock version that is not a number is a broken lock".
