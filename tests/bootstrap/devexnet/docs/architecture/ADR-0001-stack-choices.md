# ADR-0001: Stack Choices

Date: 2026-06-17
Status: Accepted

## Context

devexnet needs a CLI tool that can:
- Invoke external processes (pre-commit, shellcheck, validate_loomreed_light.sh)
- Parse YAML (DAIS agent config, loom-reed-light task files)
- Be extended incrementally without large refactors
- Be validated with a CI coverage gate

The developer machine already has Python 3.11+ available (required by DAIS).

## Decision

**Language**: Python 3.11+
- Already present in DAIS environment; no new runtime dependency
- Strong YAML support (PyYAML), subprocess handling, and Click CLI framework
- pytest ecosystem for coverage-gated testing

**CLI framework**: Click
- Subcommand routing is clean and testable (Click's test runner)
- `--help` generation is automatic from docstrings
- No global state; commands are plain functions

**Config parsing**: PyYAML
- Already used by DAIS pre-execution validator
- Consistent library across the stack

**Testing**: pytest + pytest-cov
- Coverage threshold enforced at 80% (statements)
- Fixtures isolate file I/O from domain logic

**Linting**: ruff
- Fast, single-tool replacement for flake8 + isort + pyupgrade
- Zero config needed for most projects

## Consequences

- All subprocess calls must go through `src/runner.py` to keep the domain layer testable
- Click test runner enables unit testing of CLI behavior without spawning a subprocess
- PyYAML safe_load is the only permitted YAML loading function (no yaml.load)
