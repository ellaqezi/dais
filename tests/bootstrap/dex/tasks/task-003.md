## Summary

Implement `dex bootstrap <target-dir>` subcommand: invokes the DAIS three-phase
pipeline out-of-process on the target directory, then writes loom-reed-light
spec/tasks scaffold and a CLAUDE.md stub at the project root.

## Spec Links

- spec/devex-integration.md#bootstrap
- spec/architecture.md#constraints (subprocess isolation via dex/runner.py)

## Acceptance Criteria

- `dex bootstrap <path>` runs derive-agent, gates on manifest-agent CONFIRM, then
  executes bootstrap agents — all invoked as out-of-process calls via dex/runner.py
- `dex bootstrap <path>` creates spec/ and tasks/task-list.md at target root if absent
- `dex bootstrap <path>` writes CLAUDE.md at target root (idempotent: no overwrite if present)
- Running bootstrap twice on the same target produces the same result (idempotent)
- Prompt content is never interpolated into shell arguments; path args go through
  pathlib.Path.resolve() and are validated to stay within target root
- Exit code 0 only if all three DAIS phases complete without error

## Impact

- New: dex/runner.py (subprocess isolation module — prerequisite for this and task-004)
- New: dex/io.py (all file reads/writes)
- Modifies: dex/main.py (wire bootstrap command to pipeline module)
- New: tests/test_bootstrap.py

## Size

M

## Status

not-started

## Test Plan

- Unit: mock runner.py calls; assert derive → manifest → execute call sequence
- Unit: mock io.py; assert CLAUDE.md and spec/ written with correct content
- Integration: run against tests/bootstrap/dex itself; assert idempotent on second run
- `dex bootstrap --help` shows TARGET_DIR argument and description

## Notes

Blocked on: dex/runner.py must exist first (shared with task-004).
dex/runner.py should be created as the first step of whichever of task-003/task-004
is implemented first — the other task picks it up as a dependency.
