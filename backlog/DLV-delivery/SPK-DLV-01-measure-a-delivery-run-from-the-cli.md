---
id: SPK-DLV-01
type: spike
title: Measure a delivery run from the CLI
epic: EP-DLV
source_reqs: []
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Goal

Find out how much a delivery run costs per step from the plain `claude` CLI, compared with the Claude desktop app, so that any advice on running delivery with fewer tools loaded rests on a measurement.

## Context

- The US-DLV-38 run (2026-11-26, desktop app) cost about 2.37M effective tokens, counting cache reads at 0.1×, cache writes at 2×, and output at 5× an input token. Each of its 69 steps re-read a base of about 79k tokens, of which about 18.9k were loaded tool definitions, mostly the desktop app's own tools; the connector tools were deferred and cost little.
- Documented on code.claude.com (mcp page, checked 2026-11-26): `--strict-mcp-config` loads only the servers passed with `--mcp-config`; `disableClaudeAiConnectors` turns off claude.ai connectors.
- Unmeasured: how large the per-step base is from the CLI.

## Done when

- A ticket of similar size is delivered from the `claude` CLI and measured the same way, and Findings record its per-step base, its total, and both Claude Code versions.
- If the CLI run is meaningfully cheaper, a follow-up ticket is filed to document lean delivery runs in `CONTRIBUTING.md`; otherwise Findings say no follow-up is needed.

## Findings
