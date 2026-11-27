# Delivery record: chore/usage-report

- Branch: `chore/usage-report`
- Ticket: None

Written by `scripts/deliver.py record`. Everything below the marker is the change request's description, verbatim; `deliver.py gate pr` fails when it differs from the current description.

<!-- change-request-description -->

## Ticket

None. Adds `tools/usage_report.py`, this repository's cost report for Claude Code sessions, as decided in "A cost report for this repository's delivery runs" (a `chore/` change by decision; not part of the product).

## Plan

No ticket, so no criterion rows. Built against the decision-log entry: the tool reads a session transcript and its subagents' transcripts and prints raw tokens, effective tokens weighted by a per-model table from the pricing page (URL and date in the script), the share per group, the call count, and the peak context; `--json` for before-and-after comparisons; a clear stop when a field it needs is missing. `tools/README.md` documents it; `tests/test_usage_report.py` builds synthetic transcripts only.

Checked on the real US-DLV-38 transcript (not committed): 1,606,181 effective tokens, matching the corrected figure in "The US-DLV-38 run cost about 1.61M effective tokens, not 2.37M".

Constrained by: the decision-log entry above; `AGENTS.md`, "This project" (standard library, Python 3.9+, English, no local paths).

## Gaps found

- None

## Decisions

- How the tool groups and checks a transcript (the two extra groups, which `deliver.py` calls count as gates, how responses and missing fields are handled). Log: How the cost report groups and checks a transcript

## Platform changes

- None

## Test changes

None (no frozen tests; `tests/test_usage_report.py` is new and untagged, as the tool proves no ticket criterion).

## Review report

Three fresh-context reviews in diff mode, against the decision-log entry in place of ticket criteria.

**First review (commit e129a57): CRITICAL: 0, WARNING: 2, SUGGESTION: 3.**
- WARNING: a call's own output entered the context before the call was charged. Fixed: content a call writes enters after it; test added.
- WARNING: missing cache fields became 0. Fixed: the tool stops; test added.
- SUGGESTION: two groups beyond the decision's list. Fixed: documented in the README and logged.
- SUGGESTION: compaction skews the groups. Fixed: documented in the README.
- SUGGESTION: a subagent with no model call stopped the whole report. Fixed: listed as skipped; test added.

**Second review (commit bae73f7): CRITICAL: 0, WARNING: 3, SUGGESTION: 3.**
- WARNING: cache writes without their 5-minute/1-hour split were priced as 5-minute writes. Fixed: the tool stops; test added.
- WARNING: `deliver.py context`, `next`, `status`, `pr-body` counted as gates. Fixed: only `gate` and `check`; tests added.
- WARNING: the extra groups were not in the decision log. Fixed: entry "How the cost report groups and checks a transcript".
- SUGGESTION: a block repeated across one response's records was counted twice. Fixed; test added.
- SUGGESTION: git commands naming a framework file counted as framework reading; non-UTF-8 files and non-dict blocks crashed. Fixed; tests added.
- SUGGESTION: mention `tools/` in `AGENTS.md`, "This project". Not taken: `AGENTS.md` edits need the owner, and `tools/README.md` documents the tool.

**Third review (commit 72d15f6): CRITICAL: 0, WARNING: 1, SUGGESTION: 3.**
- WARNING: the log entry said "the test runners" count as gates, but the tool matches only `python3 -m unittest` and `python3 -m pytest`. Fixed in the entry's wording (commit after the reviewed one, `docs/decision-log.md` only): that is how this repository runs its tests.
- SUGGESTION: repeated records of one response might carry partial usage. Not changed: checked on the real US-DLV-38 transcript, repeated records carry identical usage.
- SUGGESTION: heredoc `.replace(` and `cat > f <<EOF` can be misgrouped. Not changed: they shift only the estimated groups, which the report states are estimates.
- SUGGESTION: confirm the 0.05 cache-read multiplier for Opus 5.5 and Sonnet 5.5. Not changed: confirmed on the pricing page on 2026-11-27 before the define change.

Reviewed commit: 72d15f66de8cb9638b162a2862f8f47dbf937c0d
CRITICAL: 0, WARNING: 1, SUGGESTION: 3

## Checks

- `python3 scripts/deliver.py check` on commit 72d15f6: PASS, 316 tests (pytest from a throwaway virtualenv, as CI installs it; this machine's Python has no pytest).
- `python3 -m unittest tests.test_usage_report`: 16 tests OK.
- `python3 scripts/backlog_check.py`: 0 errors, 0 warnings.
- By hand: the tool on the US-DLV-38 transcript prints 1,606,181 effective tokens.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
