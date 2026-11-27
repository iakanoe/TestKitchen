# Tools

Developer tools for working on Test Kitchen itself. They are not part of the product: nothing here is in `template/`, `init.py` never installs it, and it sits outside the `code` globs in `kitchen.yml`.

## `usage_report.py`

Reports where a Claude Code session's tokens went, so a delivery run can be measured the same way before and after a change (decision log, "A cost report for this repository's delivery runs"; SPK-DLV-01).

```bash
python3 tools/usage_report.py ~/.claude/projects/<project>/<session-id>.jsonl
python3 tools/usage_report.py ~/.claude/projects/<project>/<session-id>.jsonl --json > before.json
```

`<project>` is the session's working directory with every non-alphanumeric character replaced by `-`. The subagents' transcripts in `<session-id>/subagents/` are read too.

For the session and each subagent it prints the raw token counts, effective tokens (each count weighted by the model's price multiplier; the table and its source are at the top of the script), the share per group, the number of model calls, and the peak context.

- **The groups are estimates.** A model call reports only totals, so each call's input is split by the estimated share of each kind of content in its context. The counts and weights are exact.
- **The transcript format can change.** Claude Code documents it as internal and liable to break on any release. When a record lacks a field the tool needs, it stops with a message instead of printing a wrong number.
- **Prices change.** Update `PRICES` from the pricing page, with the date checked, when a new model is used or a price moves. A model missing from the table is reported, and default multipliers are used for it.
- **Never commit a real transcript**, here or in a test: it holds the session's full conversation. The tests build small synthetic ones.
