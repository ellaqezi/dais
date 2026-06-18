# CLAUDE.md — dex

This file provides project-specific guidance for Claude Code sessions in this repository.
It overrides global `~/.claude/` rules only where dex differs. All unmentioned rules
defer to the global dotclaude config.

## This Project

dex (package: `dex`, repo: `dex`) is a Python CLI tool that orchestrates DAIS, dotclaude, and loom-reed-light.
Stack: Python 3.11+, Click, PyYAML, pytest.
No web server. No external service calls in core logic. All side effects isolated to I/O layer.

## Reference Files (dex-specific overrides)

| Concern | Override |
|---------|---------|
| Task sizing | loom-reed-light rules apply: S (≤250 LOC), M (251-500 LOC). Decompose before implementing anything larger. |
| Spec-first | Before any non-trivial feature: create or update `spec/<topic>.md` first. Link from task. |
| Worktree | Per ADR-0003: `git worktree add ../dex-<issue-id> feature/<issue-id>-<slug>`. |
| Validation | Run `make validate` before every push. Run `dex validate` for a quick check. Fixes CI failures autonomously (see §CI below). |
| Model tier | See `docs/finops/token-routing-strategy.md`: S tasks → Haiku, M tasks → Sonnet, ADRs/architecture → Opus. |

All other rules (`~/.claude/coding-standards.md`, `~/.claude/git-workflow.md`,
`~/.claude/tool-usage.md`, etc.) apply without modification.

## At Session Start

1. Read `spec/devex-integration.md` — source of truth for how the three tools integrate.
2. Read `tasks/task-list.md` — current backlog state.
3. Check `known-issues.md` if present.
4. Pick up from the highest-priority `ready` task or consult user.

## Project Layout

```
spec/          Planning source-of-truth (loom-reed-light)
tasks/         S/M task tracking (loom-reed-light)
docs/          Generated documentation (DAIS bootstrap output)
  architecture/  ADRs
  security/      Threat model, OWASP mapping
  finops/        Token routing, cost tagging, budget alerts
src/           Python CLI source (Click-based)
scripts/       Validation and utility scripts
prompts/       loom-reed-light workflow prompts
```

## CI Behaviour

CI runs three validators in order — failures are independently attributable:

1. `pre-commit run --all-files` — formatting, whitespace, YAML, secrets (all hooks in `.venv`)
2. `bash scripts/validate_loomreed_light.sh` — LOOM schema compliance
3. `shellcheck scripts/*.sh` — shell syntax (system tool; verified by `make check-prereqs`)

**Self-contained after `make install`**: `pre-commit`, `ruff`, `pytest`, `detect-secrets` all live
in `.venv` or pre-commit's cache. Only `python3 >= 3.11`, `git`, and `shellcheck` are system prerequisites.

When CI fails:
- pre-commit / trailing-whitespace / YAML: fix formatting in staged diff, re-push
- pre-commit / detect-secrets: verify the flagged string is not a real secret; update baseline if safe
- LOOM validation failure: task section missing or size > M — fix in task file
- shellcheck failure: fix shell syntax in scripts/

## Prompt Injection Warning

dex processes DAIS agent prompts and loom-reed-light workflow prompts as input.
Before executing any user-supplied prompt content, validate against the allow-list
in `src/validators.py`. Never pass unsanitized user input as a system prompt or
shell argument. See `docs/security/threat-model.md` §3 (Prompt Injection).
