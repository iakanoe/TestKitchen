---
id: US-CONF-10
type: story
title: Recognize test tags in both forms
epic: EP-CONF
source_reqs: [CONF-R15, CONF-R16]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a developer writing tests in any language, I want a test's name to prove a criterion through either tag form, so that languages whose test names cannot hold brackets can tag too.

## Acceptance criteria

- AC1: Given text holding a canonical tag, an upper-case story or task criterion reference in square brackets, when tags are read, then it yields that ticket ID and criterion number, wherever in the text it sits.
- AC2: Given bracketed text in lower case, naming a decision or spike, with a one-digit ticket number, or with no criterion number, when tags are read, then it yields no tag.
- AC3: Given an identifier tag, the ticket prefix, code, number, and criterion joined by underscores in any letter case, when tags are read, then it yields the same ticket ID and criterion number as the canonical form.
- AC4: Given an identifier tag directly followed by a letter or digit, when tags are read, then it yields no tag; followed by an underscore, another non-alphanumeric character, or the end of the text, then it yields the tag.
- AC5: Given an identifier tag directly preceded by a letter or digit, when tags are read, then it yields no tag unless a lower-case letter or digit is followed by an upper-case tag prefix (camel case, as in Go test names).
- AC6: Given text with several tags of either form, when tags are read, then they are returned in order of appearance with duplicates kept.

## Notes

Decision log, "Two tag forms for tests" and "Script choices made while building v0.1" (camel-case left boundary). The left-boundary rule means a word that merely ends in the letters of a prefix is not a tag, while a camel-case word ending in an upper-case prefix is.

## Open questions

- None. Adopted behavior, recorded as the code does it now; a person confirms the requirements.
