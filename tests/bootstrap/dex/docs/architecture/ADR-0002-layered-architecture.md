# ADR-0002: Layered Package Architecture

Date: 2026-06-17
Status: Accepted

## Context

As dex grows beyond a single-file CLI, business logic, I/O, and subprocess calls
risk becoming entangled in `dex/main.py`. Click commands are difficult to unit-test
when they contain file operations or subprocess calls directly — the only entry point
is Click's test runner, which cannot easily mock filesystem or process state.

## Decision

**Three-layer architecture with strict import boundaries:**

```
CLI layer      dex/main.py
               Click commands only. No file I/O. No subprocess. No business logic.
                   |
Domain layer   dex/pipeline.py  dex/validators.py  dex/tasks.py
               Pure functions. No Click imports. No file opens. No subprocess.
                   |
I/O layer      dex/io.py        dex/runner.py
               All file reads/writes (io.py). All subprocess calls (runner.py).
               These are the only modules with side effects.
```

**Enforcement rules:**
- `dex/main.py` may import from domain layer and `click` only
- Domain layer modules must not import `click`
- `dex/io.py` is the only module that opens files
- `dex/runner.py` is the only module that calls `subprocess`

## Consequences

- Click test runner (CliRunner) can test CLI routing without mocking I/O
- Domain layer is fully unit-testable with plain `pytest` fixtures — no subprocess or filesystem
- `dex/runner.py` and `dex/io.py` are the only modules requiring integration tests
- New features follow the same boundary: add domain logic to domain layer, wire in CLI layer
- Boundary violations are detectable by import analysis (ruff or grep in CI)
