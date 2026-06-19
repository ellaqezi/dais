# Spec: DevEx Integration

## Goal

dex is a CLI tool for orchestrating three developer-experience frameworks — DAIS,
dotclaude, and loom-reed-light — as a unified, coherent development stack.

The goal is to eliminate the friction of context-switching between the three tools by
providing a single entry point for bootstrapping, auditing, validating, and status checks.

## Behavior

### Bootstrap (`dex bootstrap [target-dir ...]`)

- Accepts one or more target directories; defaults to `.` when none given
- **Fail-fast**: stops on the first directory that fails (manifest CONFIRM is interactive;
  batching past a rejection is unsafe)
- Runs the DAIS three-phase pipeline on each `<target-dir>`:
  1. derive-agent: scans for topology, stack, PII, DPIA triggers
  2. manifest-agent: presents plan, waits for CONFIRM
  3. execute phase: runs all relevant bootstrap agents in order
- Creates loom-reed-light spec/ and tasks/ structure as a post-bootstrap step
- Writes CLAUDE.md at project root pointing to dotclaude guides

### Audit (`dex audit [target-dir ...]`)

- Accepts one or more target directories; defaults to `.` when none given
- **Run-all**: continues across all directories; prints a per-directory summary and
  exits non-zero if any directory failed
- Runs DAIS audit pipeline: audit-agent -> gap-agent -> remediation-agent
- Outputs gap register to stdout and writes `gap-register.md` at each target root
- Does not modify target project without explicit `--apply` flag

### Validate (`dex validate [target-dir ...]`)

- Accepts one or more target directories; defaults to `.` when none given
- **Run-all**: continues across all directories; prints a per-directory summary and
  exits non-zero if any directory failed
- Runs all three validators in order for each target:
  1. pre-commit hooks
  2. LOOM schema validator (task sections, status, sizing)
  3. shellcheck on scripts/
- Each failure is independently labelled with its directory and validator layer

### Status (`dex status [target-dir ...]`)

- Accepts one or more target directories; defaults to `.` when none given
- **Run-all**: reads `tasks/task-list.md` in each target and prints a per-directory
  summary; exits 0 even if a target has no task list (prints a "no task list" notice)

## Multi-Target Output Format

When multiple directories are given, each directory's output is framed with a header
and a per-directory result line. A summary line closes the command:

```
[dex] audit: path/to/dir-a
  ...

[dex] audit: path/to/dir-b
  ...

Summary: 2 target(s) — N passed, M failed
```

Exit code is 0 only if all targets passed.

## Constraints

- No external API calls from the CLI itself. Agent interactions are out-of-process.
- All file mutations are idempotent: running bootstrap twice produces the same result.
- Prompt content is never passed directly to a shell command or external process.
  All user-supplied input is validated against an allow-list before use.
- S/M task sizing applies to all dex features: decompose before implementing.

## Acceptance Criteria

- `dex --help` lists all four subcommands with descriptions
- `dex validate` exits 0 on a clean project, non-zero with labeled errors on failure
- `dex status` reads task-list.md and prints a correct status summary
- All prompt files in prompts/ are listed in AGENTS.md command table
- No hardcoded credentials anywhere in codebase (verified by detect-secrets baseline)

## Open Questions

- Should `dex bootstrap` write AGENTS.md and loom-reed-light prompts to target project,
  or only DAIS outputs? (Decision: yes — full integration, not partial)
- Should `dex audit` require an existing spec/ directory, or create one on first run?
  (Decision: create on first run with derive-agent output as initial spec content)
