## Summary

Implement `devexnet validate [target-dir]` subcommand: runs the three-layer validation
stack (pre-commit, LOOM schema, shellcheck) in sequence and reports failures
with per-layer attribution.

## Spec Links

- spec/devex-integration.md#validate
- spec/architecture.md#constraints (subprocess isolation via src/runner.py)

## Acceptance Criteria

- `devexnet validate` with no arguments validates the current working directory
- `devexnet validate <path>` validates the specified directory
- Each validator runs in order: pre-commit → LOOM schema → shellcheck
- On failure, output clearly labels which validator failed and why
- Exit code is 0 only if all three validators pass
- `devexnet validate` on a clean project (this repo) exits 0

## Impact

- Modules/Files/Tests: src/validators.py, tests/test_validators.py (new)
- Modifies: src/main.py (wire up validate command to validators module)

## Size

M

## Status

ready

## Test Plan

- `dex validate` on this project exits 0 after `make validate` passes
- Unit test: mock runner.py calls; verify correct sequence and exit-code propagation
- Integration test: introduce a deliberate task-section gap → LOOM validator fails
  → exit code non-zero, output attributes failure to LOOM schema layer

## Notes

- pre-commit requires an installed .git hook; validate must handle the case where
  pre-commit hooks are not installed (warn, don't hard-fail — not all users run git)
- shellcheck must handle missing scripts/ directory gracefully (no-op)
