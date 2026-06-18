# Contributing to devexnet

## Ground Rules

- Every non-trivial feature starts with a spec in `spec/<topic>.md`.
- All work is decomposed into S (≤250 LOC) or M (251–500 LOC) tasks before implementation.
- Commits follow conventional commits format: `type(scope): subject`.
- Pre-push Opus review (3 clean passes) is mandatory before every push.
- Never push directly to `main`. All work goes through a feature branch on a worktree.

## Worktree Workflow (ADR-0003)

For every issue or task:

```bash
# Create a worktree for the issue
git worktree add ../devexnet-<issue-id> feature/<issue-id>-<slug>
cd ../devexnet-<issue-id>

# Work on the feature (spec → refine → implement)
# Run validation before pushing
make validate

# Push and open PR
git push -u origin feature/<issue-id>-<slug>
gh pr create --fill

# After merge, clean up
cd ../devexnet
git worktree remove ../devexnet-<issue-id>
```

## Branch Taxonomy

| Prefix | Use |
|--------|-----|
| `feature/` | New feature or capability |
| `fix/` | Bug fix |
| `chore/` | Tooling, deps, config with no behavior change |
| `release/` | Release preparation |

## Pre-commit Setup (once per clone)

```bash
brew install pre-commit    # or: pipx install pre-commit
pre-commit install
pre-commit run --all-files
```

## Validation

```bash
make validate    # runs pre-commit + LOOM schema + shellcheck
```

Fix all errors before opening a PR. Validator failures in CI are attributable:
- **pre-commit**: formatting or secret in staged diff
- **LOOM schema**: missing task section, invalid status, or size > M
- **shellcheck**: shell syntax error in scripts/

## PR Checklist

- [ ] Spec created or updated in `spec/` if behavior changed
- [ ] Tasks in `tasks/` updated (status, size, spec links)
- [ ] `tasks/task-list.md` synchronized with task detail files
- [ ] `AGENTS.md` updated if new loom-reed-light command added
- [ ] `make validate` passes locally
- [ ] 3-pass Opus pre-commit review completed

## Commit Message Format

```
type(scope): subject under 72 chars

- Why this change is needed (not what it does)
- Trade-offs or alternatives considered
```

Never include Co-Authored-By or mention Claude/Anthropic in commit messages.
Write commit messages to `/tmp/claude/commit-<slug>.txt`, commit with `git commit -F`, delete after.
