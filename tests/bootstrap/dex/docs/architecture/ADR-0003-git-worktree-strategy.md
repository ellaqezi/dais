# ADR-0003: Git Worktree Strategy

Date: 2026-06-17
Status: Accepted

## Context

Concurrent feature development on devexnet risks context bleed between branches: stashed
work, partial changes, and accidental staging of unrelated files. Standard branch-switching
on a single working tree amplifies this when an agent is mid-task.

## Decision

**Worktree-per-issue**: every non-trivial change gets its own working tree.

```bash
# Start an issue
git worktree add ../devexnet-<issue-id> feature/<issue-id>-<slug>
cd ../devexnet-<issue-id>

# Work, validate, push
make validate
git push -u origin feature/<issue-id>-<slug>
gh pr create --fill

# After merge, clean up
cd ../devexnet
git worktree remove ../devexnet-<issue-id>
```

## Branch Taxonomy

| Prefix | Use | Merges to |
|--------|-----|-----------|
| `feature/` | New capability | main via PR |
| `fix/` | Bug fix | main via PR |
| `chore/` | Config, deps, tooling | main via PR |
| `release/` | Release prep | main via PR |

## Trivial-change Exemption

Changes meeting all three criteria may use the main worktree directly:
1. Affects exactly one file
2. No behavior change (typo fix, comment update, version bump)
3. CI passes in one push

## Consequences

- `git worktree list` shows active worktrees; prune regularly after merges
- Worktree directories must be siblings (e.g. `../devexnet-42`), not subdirectories
- CI watcher (per dotclaude `git-workflow.md`) is spawned once per push, not per worktree
- security-agent branch merges last per DAIS `scope-manifests.yaml` forced ordering
