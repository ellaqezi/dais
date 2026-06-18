## Summary

Scaffold the devexnet CLI package structure, entry point, and pyproject.toml.
Establishes the layered architecture defined in spec/architecture.md:
CLI layer → Domain layer → I/O layer, with subprocess isolation in runner.py.

## Spec Links

- spec/architecture.md#behavior
- spec/devex-integration.md#constraints

## Acceptance Criteria

- `dex --help` runs and lists bootstrap, audit, validate, status subcommands
- `src/main.py` imports only from `src/` domain modules and `click`
- `src/runner.py` is the only module calling `subprocess`
- `pyproject.toml` declares all runtime and dev dependencies
- `make install` creates `.venv` and installs package in editable mode

## Impact

- Modules/Files/Tests: src/main.py, src/runner.py, src/io.py, pyproject.toml, tests/test_main.py

## Size

S

## Status

done

## Test Plan

- `make install` exits 0
- `dex --help` shows four subcommands
- Each subcommand `--help` shows at minimum a description and `--help` option
- `pytest tests/test_main.py` passes

## Notes

- Click chosen per ADR-0001 for ergonomic subcommand routing and --help generation
- No business logic in main.py; each subcommand delegates immediately to domain modules
