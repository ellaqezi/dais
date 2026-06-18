## Summary

Implement `dex status` subcommand: reads tasks/task-list.md in the current
directory and prints a summary of counts by status and the next ready task.

## Spec Links

- spec/devex-integration.md#status
- spec/architecture.md#constraints (I/O isolated to dex/io.py)

## Acceptance Criteria

- `dex status` reads tasks/task-list.md from the current working directory
- Output includes: count of done / in-progress / ready / not-started tasks
- Output includes: title and ID of the highest-priority ready task
- `dex status` exits 0 if task-list.md is absent (prints a "no task list found" message)
- `dex status` exits non-zero if task-list.md is present but malformed

## Impact

- Requires: dex/io.py (create here if neither task-003 nor task-004 has run first)
- New: dex/tasks.py (task-list parsing logic)
- Modifies: dex/main.py (wire status command to tasks module)
- New: tests/test_status.py

## Size

S

## Status

todo

## Test Plan

- Unit: parse a fixture task-list.md; assert correct counts per status bucket
- Unit: missing task-list.md → exit 0, "no task list found" message
- Unit: malformed task-list.md (missing header row) → exit non-zero
- `dex status` run in this project prints task-002 as next ready task
- `dex status --help` shows description

## Notes

Smallest of the three unimplemented commands. Good candidate to implement first
to validate the dex/tasks.py + dex/io.py module boundary before tackling M-sized tasks.
Consider implementing this before task-003 or task-004 since it only needs io.py (S).
