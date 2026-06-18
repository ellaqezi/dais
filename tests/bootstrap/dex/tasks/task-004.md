## Summary

Implement `dex audit <target-dir>` subcommand: runs the DAIS audit pipeline
(audit-agent → gap-agent → remediation-agent) out-of-process on the target
directory and writes gap-register.md at the target root.

## Spec Links

- spec/devex-integration.md#audit
- spec/architecture.md#constraints (subprocess isolation via dex/runner.py)

## Acceptance Criteria

- `dex audit <path>` invokes audit-agent, gap-agent, remediation-agent in sequence
  via dex/runner.py; each agent's output is the next agent's input
- `dex audit <path>` writes gap-register.md at target root
- `dex audit <path>` prints gap register to stdout
- Target project is not modified without `--apply` flag (read-only by default)
- Path arg resolved with pathlib.Path.resolve(); validated to be an existing directory
- Exit code 0 only if all three agents complete; non-zero with labelled error otherwise

## Impact

- Requires: dex/runner.py (create here if task-003 has not run first)
- Requires: dex/io.py (create here if task-003 has not run first)
- New: dex/pipeline.py (audit pipeline orchestration)
- Modifies: dex/main.py (wire audit command to pipeline module)
- New: tests/test_audit.py

## Size

M

## Status

todo

## Test Plan

- Unit: mock runner.py calls; assert audit-agent → gap-agent → remediation-agent
  call order and that each output is passed as input to the next
- Unit: mock io.py; assert gap-register.md written to target root
- Unit: assert --apply flag absent → no writes to target project
- `dex audit --help` shows TARGET_DIR argument and description
- `dex audit /no/such/dir` exits non-zero

## Notes

Shares dex/runner.py and dex/io.py with task-003 (bootstrap).
If task-003 is implemented first, those modules already exist — skip their creation.
If this task runs first, create runner.py and io.py here as the first step.
