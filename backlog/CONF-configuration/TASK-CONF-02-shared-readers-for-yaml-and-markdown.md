---
id: TASK-CONF-02
type: task
title: Shared readers for YAML and Markdown
epic: EP-CONF
source_reqs: [CONF-R24, CONF-R25]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

The shared library imports PyYAML only when it needs it and reads Markdown the same whatever the line endings, so every tool parses tickets, records, and the decision log alike.

## Acceptance criteria

- AC1: Without PyYAML installed, loading the configuration raises a configuration error that gives the `python3 -m pip install pyyaml` command.
- AC2: Without PyYAML installed, the repository root, glob, and tag helpers still work.
- AC3: Frontmatter with Windows line endings parses the same as with Unix line endings, and text without a leading `---` block has no frontmatter.
- AC4: A delivery record's description is read after either marker line, `<!-- change-request-description -->` or `<!-- pr-description -->`, also with Windows line endings.
- AC5: Decision-log titles are read from `### YYYY-MM-DD — <title>` headings.
- AC6: A binary or unreadable file reads as nothing, and the scans skip it.

## Notes

The rules about what a valid ticket, record, or log entry must contain belong to the backlog-check and delivery epics; this task covers only the shared reading.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
