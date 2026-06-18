# ADR-0006: Multi-Target Command Invocation

Date: 2026-06-18
Status: Accepted

## Context

All four dex commands initially accepted exactly one `target_dir` argument, defaulting
to `.`. Users working across multiple projects (e.g. auditing `tests/audit/dotfiles`
and `tests/audit/loom-reed-light` in the same session) had to invoke dex once per
directory.

A variadic argument (`nargs=-1`) lets each command accept any number of directories
in a single invocation, while still defaulting to `.` when none are given.

## Decision

**All four commands accept zero or more `target_dirs`; default to `.` when none given.**

```python
@cli.command()
@click.argument("target_dirs", nargs=-1, type=click.Path(exists=True, file_okay=False))
def audit(target_dirs: tuple[str, ...]) -> None:
    dirs = target_dirs or (".",)
    ...
```

**Per-command exit-code semantics differ:**

| Command | Mode | Rationale |
|---------|------|-----------|
| `bootstrap` | **Fail-fast** | manifest-agent CONFIRM is interactive; proceeding past a user rejection on dir N to run dir N+1 is unsafe |
| `audit` | **Run-all** | No mutation by default; full picture across all dirs is more useful than stopping at first gap |
| `validate` | **Run-all** | Reporters want all failures at once; same model as `pre-commit run --all-files` |
| `status` | **Run-all** | Read-only; partial output would be confusing |

**Output format** (multi-target):

```
[dex] audit: path/to/dir-a
  ...

[dex] audit: path/to/dir-b
  ...

Summary: 2 target(s) — N passed, M failed
```

Single-target output is unchanged (no summary line).

## Consequences

- Click `nargs=-1` produces a `tuple[str, ...]`; an empty tuple means "use cwd"
- `type=click.Path(exists=True, file_okay=False)` still validates each path before the command runs; nonexistent paths exit non-zero before any work starts
- Run-all commands accumulate per-directory pass/fail and exit non-zero if any failed
- Fail-fast commands (`bootstrap`) stop at the first non-zero result
- `dex status` with no task list in a target exits 0 with a notice (not an error)
- Tests cover: single target, multiple targets (all pass), multiple targets (mixed), no-arg default
