# devexnet

A Python CLI harness that unifies three developer-experience tools — DAIS, dotclaude, and
loom-reed-light — into a single, coherent project structure.

This repository was **bootstrapped by DAIS**, **structured by loom-reed-light**, and
**governed daily by dotclaude**. Its own development is the integration demonstration.

## What This Is

| Layer | Tool | Role |
|-------|------|------|
| Compliance + bootstrap | [DAIS](../../README.md) | Generated this project's scaffold, ADRs, security threat model, CI pipeline, and finops strategy |
| Daily development | [dotclaude](../audit/dotclaude/README.md) | Governs how work is done: model tiers, worktrees, pre-push Opus review, CI watchers |
| Planning + traceability | [loom-reed-light](../audit/loom-reed-light/README.md) | Spec-to-task-to-code traceability; keeps tasks small (S/M) and traceable |

## Project Purpose

devexnet is a CLI tool for orchestrating the three-tool DevEx stack:

- `devexnet bootstrap` — runs DAIS derive → manifest → execute on a target directory
- `devexnet audit` — runs DAIS audit sequence (audit-agent → gap-agent → remediation-agent)
- `devexnet validate` — runs LOOM schema validator + DAIS pre-execution validator
- `devexnet status` — shows current task/spec/gap register state

## Architecture at a Glance

```
spec/                   Source-of-truth planning (loom-reed-light)
  devex-integration.md  Core spec: how the three tools integrate
  architecture.md       Architecture overview, linking to docs/architecture/ADRs

tasks/                  Bounded work items (loom-reed-light, S/M only)
  task-list.md          Canonical backlog index
  task-<id>.md          Detail files with required sections

docs/
  architecture/         ADRs (DAIS architecture-agent output)
  security/             Threat model + OWASP mapping (DAIS security-agent output)
  finops/               Token routing strategy + cost tagging (DAIS finops-agent output)

src/                    Python CLI source
scripts/                Validation scripts
prompts/                loom-reed-light workflow prompts
```

## Quick Start

1. **Machine setup** (once per machine): follow [dotclaude](../audit/dotclaude/README.md)
2. **Clone this repo** with standard git:
   ```bash
   git clone git@github.com:you/devexnet.git
   cd devexnet
   ```
3. **Install development dependencies**:
   ```bash
   make install
   ```
4. **Register pre-commit hooks**:
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```
5. **Run validator**:
   ```bash
   make validate
   ```

## Development Workflow

New features follow the loom-reed-light workflow:

```bash
# 1. Create or update a spec
#    "add a spec for <topic>"  → prompts/add-spec.md

# 2. Plan tasks from the spec
#    "plan next work"          → prompts/plan.md

# 3. Refine and implement (per worktree, per issue)
git worktree add ../devexnet-<issue-id> feature/<issue-id>-<slug>
#    "refine task <id>"        → prompts/refine.md
#    "implement task <id>"     → prompts/implement.md

# 4. Validate before pushing
make validate
git diff --cached                  # review staged diff (Opus, 3 passes)
git push                           # triggers CI + CodeRabbit watcher
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full worktree workflow and branch taxonomy.

## Validation

This project runs three independent validators in CI:

| Validator | What it checks | Command |
|-----------|----------------|---------|
| pre-commit | Trailing whitespace, YAML, merge conflicts, secrets | `pre-commit run --all-files` |
| LOOM schema | Task sections, status vocabulary, S/M sizing | `bash scripts/validate_loomreed_light.sh` |
| shellcheck | Shell script syntax | `shellcheck scripts/*.sh` |

Run all at once: `make validate`

## License

MIT
