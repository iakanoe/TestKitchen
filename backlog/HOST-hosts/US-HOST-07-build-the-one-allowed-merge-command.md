---
id: US-HOST-07
type: story
title: Build the one allowed merge command
epic: EP-HOST
source_reqs: [HOST-R14, HOST-R15, HOST-R16]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As the delivery workflow and the guard, I want a single merge command per host, pinned to the head commit the checks passed on, so that nothing pushed after the merge gate ran can be merged with it and no merge is deferred.

## Acceptance criteria

- AC1: Given the GitHub host, a change-request number, and a full head sha, when the merge command is built, then it is `gh pr merge <n> --merge --match-head-commit <sha>`.
- AC2: Given the GitLab host, a change-request number, and a full head sha, when the merge command is built, then it is `glab mr merge <n> --sha <sha> --auto-merge=false --yes`.
- AC3: Given a change-request number that is not a positive integer (zero, empty, or with other characters such as a shell separator), when the merge command is built, then ValueError is raised.
- AC4: Given a head sha that is not 40 lowercase hexadecimal characters (short, uppercase, or a name such as HEAD), when the merge command is built, then ValueError is raised.
- AC5: Given a number with surrounding spaces or leading zeros, when the merge command is built, then the command carries the plain number.
- AC6: Given a change-request number that is not a positive integer, when a change request is read on GitHub or GitLab, then ValueError is raised before any host CLI runs.

## Notes

- On GitLab the merge method is the project's setting, which must be "Merge commit" (the story on host settings and the guide).
- `deliver.py merge-command` prints this command and the guard allows a merge only when it matches word for word; both belong to other epics.
- AC2 has never run against a real `glab` (SPK-HOST-01).
- A sha followed by a newline passes AC4's check today: DEC-HOST-02.

## Open questions

- None. Adopted behavior, recorded as it is; the open points are tracked in the epic's decision and spike tickets.
