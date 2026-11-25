---
id: US-DEF-19
type: story
title: Start define in the right mode
epic: EP-DEF
source_reqs: [DEF-R26, DEF-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a person defining a product, I want `/define` to pick or run the right mode, so that I start where my project actually is.

## Acceptance criteria

- AC1: Given `/define` with a mode and a topic, or a request to follow the playbook in a named mode, when the agent starts, then it runs that mode on that topic.
- AC2: Given no mode and a `docs/product.md` with only headings and comments, when the agent starts, then it runs `new`.
- AC3: Given no mode, code in the repository, and no ticket under `backlog/`, when the agent starts, then it offers `adopt`.
- AC4: Given no mode in any other case, when the agent starts, then it runs `backlog_check.py --gaps`, summarizes it in one line, and asks whether to run `change`, `refine`, or `sweep`.
- AC5: Given Claude Code and a decision to ask, when the skill asks it, then it writes the decision brief and asks with AskUserQuestion, one question per decision, the recommendation first and marked "(recommended)".
- AC6: Given Claude Code running headless, when the skill reaches a question, then it prints the decision briefs and questions, writes nothing that needs a yes, and stops.

## Notes

- Adopted 2026-11-25 from existing behavior: playbook behavior (`playbooks/define.md`): an agent following it does this, so its criteria are verified by review, not by tests; the Claude Code mechanics are in `.claude/skills/define/SKILL.md`.
- The criteria describe what happens now; confirmation happens on the cited `(observed in code)` requirements.

## Open questions

- None. This story records behavior that already exists; anything that looks unintended is filed as a decision on the epic.
