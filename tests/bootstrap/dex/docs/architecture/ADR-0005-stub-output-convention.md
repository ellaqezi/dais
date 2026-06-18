# ADR-0005: Stub Output Convention and --verbose Reservation

Date: 2026-06-18
Status: Accepted

## Context

Before commands are implemented, their stubs need to communicate clearly without
misleading the user. Two anti-patterns were encountered during development:

**Anti-pattern 1 — terse internal notes as output:**
```
[dex] audit: . (not yet implemented — task-004)
```
This tells the user nothing actionable. The task reference is opaque and the user
has no way to know what to do next or where to look.

**Anti-pattern 2 — --verbose printing pipeline descriptions:**
A `--verbose` flag was added to stubs to print detailed pipeline descriptions.
This produced output that looked functional but ran nothing:
```
$ dex audit --verbose tests/audit/dotfiles
[dex] audit: tests/audit/dotfiles

Pipeline (when implemented):
  1. audit-agent       — scan the project for architectural and compliance gaps
  ...
```
This misappropriates `--verbose` — the flag conventionally controls the verbosity
of *real execution*, not the description of *future* execution. A user encountering
this output would reasonably believe `--verbose` was running something.

## Decision

**Stub output convention (three lines, no flags):**
```
[dex] <command>: <target>
  Not yet implemented  →  ./tasks/task-NNN.md
  Interim: <exact command the user can run right now>
```

**`--verbose` / `-v` reservation:**
- `--verbose` is not defined on any stub command
- Passing `--verbose` to a stub exits non-zero ("No such option")
- The flag is added only when the command is implemented, where it controls
  real output verbosity (e.g. suppress/show agent stdout)

**Task file paths** use `./tasks/` prefix — Cmd+clickable in VS Code terminal and
iTerm2 without special encoding.

## Consequences

- Stubs are honest: they make no promise of execution
- Users get an immediate workaround (`make validate`, `cat tasks/task-list.md`, etc.)
- `--verbose` passed to an unimplemented command correctly signals "not yet available"
- When a command is implemented, adding `--verbose` is a deliberate, visible act
- Tests enforce both properties: `test_stub_output` and `test_unknown_flag_exits_nonzero`
