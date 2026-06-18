# Spec: Architecture

## Goal

Establish the architectural boundaries and design decisions for dex so future
feature work stays coherent with the bootstrap intent.

## Behavior

dex follows a layered CLI architecture:

```
CLI layer      (dex/main.py — Click commands: bootstrap, audit, validate, status)
    |
Domain layer   (dex/pipeline.py, dex/validators.py, dex/tasks.py)
    |
I/O layer      (dex/io.py — all file reads/writes isolated here)
```

No business logic in the CLI layer. No I/O in the domain layer. Side effects are
contained at the boundaries.

## Key Decisions

See detailed decision records in `docs/architecture/`:

| ADR | Decision |
|-----|---------|
| [ADR-0001](../docs/architecture/ADR-0001-stack-choices.md) | Python CLI with Click; PyYAML for config; pytest for testing |
| [ADR-0002](../docs/architecture/ADR-0002-layered-architecture.md) | Three-layer architecture: CLI → domain → I/O with strict import boundaries |
| [ADR-0003](../docs/architecture/ADR-0003-git-worktree-strategy.md) | Worktree-per-issue branch strategy |
| [ADR-0004](../docs/architecture/ADR-0004-package-name-matches-project.md) | Package directory named `dex/` not `src/` — prevents ModuleNotFoundError from any cwd |
| [ADR-0005](../docs/architecture/ADR-0005-stub-output-convention.md) | Stub output: task link + interim command; `--verbose` reserved for real implementation |
| [ADR-0006](../docs/architecture/ADR-0006-multi-target-invocation.md) | Multi-target `nargs=-1`; bootstrap=fail-fast, audit/validate/status=run-all |

## Constraints

- Domain layer must not import Click (no coupling to CLI framework in business logic)
- I/O layer provides path-based interfaces; domain layer works with in-memory objects
- All external tool invocations (pre-commit, shellcheck, validate_loomreed_light.sh)
  go through a single `dex/runner.py` module that captures output and exit codes

## Acceptance Criteria

- Domain layer has zero imports from `click`
- I/O layer is the only module that opens files
- `dex/runner.py` is the only module that calls `subprocess`
