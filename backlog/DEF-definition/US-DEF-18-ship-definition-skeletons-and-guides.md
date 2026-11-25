---
id: US-DEF-18
type: story
title: Ship the definition skeletons and guides
epic: EP-DEF
source_reqs: [DEF-R24, DEF-R25]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person installing Test Kitchen, I want empty definition files that explain their own format, and guides that explain the definition workflow, so that I and my agents know what to write where.

## Acceptance criteria

- AC1: Given a fresh install, when `docs/product.md` is opened, then it holds the headings Vision, Users and roles, Capabilities, and Boundaries with only comments under them.
- AC2: Given a fresh install, when `docs/requirements/README.md`, `docs/architecture/README.md`, and `docs/decision-log.md` are opened, then each holds a heading and a comment describing its file format, the architecture one also an Index section.
- AC3: Given a fresh install, when `backlog/README.md` is opened, then it states the layout, ticket types, frontmatter, readiness, bodies, criteria, open questions, rules, test tags and code trace, and delivery records.
- AC4: Given a person reading `guide/define.md`, when they look for how to define the product, then it explains the nine modes, how the agent asks, checkpoints, splitting, adoption, and the list of what "fully defined" requires.
- AC5: Given a person reading `guide/concepts.md`, when they look up a definition term, then it explains the product file, requirement markers, ADRs, the decision log, ticket types and fields, readiness, criteria, open questions, test tags, and code trace.

## Notes

- Adopted 2026-11-25 from existing behavior: Document behavior in `template/docs/`, `template/backlog/README.md`, `guide/define.md`, and `guide/concepts.md`; except where a test reads the skeleton, its criteria are verified by review.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
