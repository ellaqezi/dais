# Issue -> PR Autopilot (scheduled, per-repo)

A continuous delivery loop driven by GitHub issue labels. A scheduled **remote**
Claude Code agent (created via the `schedule` skill / `RemoteTrigger`) fires on a
cron, opens PRs for unlabelled issues, and stamps labels that act as the state
machine. The label *is* the dedup guard.

This file is the source of truth for the per-repo config and the routine prompt
(`issue-pr-autopilot.prompt.md`, same directory). It composes existing machinery,
it does not duplicate it:

- Selection / triage rubric -> `triage.md` (work selection + label rubric)
- Plan -> worktree -> implement -> review -> PR -> `CLAUDE.md`, `worktrees.md`,
  `coding-standards.md`, `conventions.md`
- Commit/PR hygiene + post-PR CR loop -> `git-workflow.md`
- Driving an opened PR to merge-ready -> the `pr-iterate` flow (`commands/` / skills)

> **Runtime caveat (load-bearing):** remote scheduled agents run in Anthropic's
> cloud, isolated, with their **own git checkout and zero access to a developer's
> `~/.claude`**. The design solves this with **two git sources**: the target repo
> **and** `LeanerCloud/dotclaude` (this repo). The cold agent reads the full
> guideline set (git-workflow, triage, coding-standards, conventions, worktrees,
> pr-iterate) from the `dotclaude` checkout, plus the target repo's own
> `CLAUDE.md`/`CONTRIBUTING.md` for repo-specifics. The routine prompt also inlines
> the global hard constraints as a backstop. Keep `dotclaude` and each target
> repo's committed conventions current.

## The label state machine

| Issue state | Label(s) | Meaning | Loop action |
|---|---|---|---|
| fresh / unlabelled | (none) | no PR yet | **eligible** - open a PR, then add `pr-created` |
| PR in flight | `pr-created` | a PR exists (open or merged) | skip (dedup) |
| PR merged | `pr-created` + `pr-merged` | delivered | skip; reconcile only |
| abandoned PR | `pr-created` (manual) | prior PR closed unmerged | skip (operator handles manually) |

- `pr-created` (color `1D76DB`): a PR has been opened for this issue.
- `pr-merged` (color `0E8A16`): the issue's PR has been merged.

Labels are created on first fire if missing.

## Watcher model (scheduled context differs from a local session)

The remote run has tools `[Bash, Read, Write, Edit, Glob, Grep]` only - **no Agent/Task
tool**, and any background process dies when the bounded run ends. So the agent
**cannot spawn `cr-watch`/`ci-watch` background agents**; the local git-workflow.md
"spawn a watcher" steps do not apply literally. The atomic-coupling invariant (never
request a CR review without a watcher that acts on the response) is satisfied
**structurally**: every PR triggered/re-pinged stays in the in-flight set
(`pr-created`, not `pr-merged`, PR open) and is therefore guaranteed to be
re-examined by the next hourly fire's advance phase. **The cron is the durable
watcher.** Invariant kept: only trigger/re-ping CR on a PR that remains tracked. CR
rate-limit recovery uses `@coderabbitai full review` (not the incremental form).

## Per-fire phases (CREATE before ADVANCE, so create is never starved)

0. **Preflight (cheap gate).** Resolve repo + login. Ensure both labels exist.
   Count open issues lacking `pr-created`. If 0 and nothing to reconcile, exit.
1. **Reconcile (cheap).** For each `pr-created` and not `pr-merged` issue, find its
   linked PR (closing-keyword / `(#N)` / title-mirror in a PR body, since CUDly PRs
   target a non-default base so auto-close does not fire). If MERGED, add
   `pr-merged`. Never remove `pr-created`.
2. **Create (guaranteed; cap 3).** Select top-3 eligible issues (priority -> urgency
   -> impact -> unblocks -> effort). For each: plan; branch off the base; implement;
   five-dimension self-review; conventional commit via `git commit -F`; open a PR
   with `Closes #<issue>`; **strip any auto-injected Claude footer**; **mirror the
   issue's triage rubric onto the PR**; add `pr-created` to the issue; trigger
   `@coderabbitai review` (watcher is structural - next fire's advance re-examines);
   bounded single 5-minute in-run wait to catch a fast CR response.
3. **Advance (best-effort; ALL in-flight, no hard cap).** After create, drive every
   open in-flight PR (incl. human-authored) one CR round closer to merge-ready via
   pr-iterate, in priority order, rotating across fires. **Active-human guard:** skip
   (defer) a PR whose latest commit is a human push newer than the last CR review.
   Stop when budget is low and log the rest as deferred. Never self-merge.
4. **Hand off.** A human merges. The next fire's Phase 1 stamps `pr-merged`.

## Per-repo config

| Repo | Base branch | Eligibility | New-PR cap/fire | CR-advance cap/fire | Cadence | Status |
|---|---|---|---|---|---|---|
| `LeanerCloud/CUDly` | `feat/multicloud-web-frontend` | any `triaged` issue except `type/question`, `status/blocked`, `status/needs-info` | 3 | none (all open PRs) | hourly (`0 * * * *` UTC) | disabled (pending validation) |
| other `LeanerCloud/*` | repo default unless stated | TBD | TBD | TBD | TBD | pending |
| `cristim/*` | repo default | TBD | TBD | TBD | TBD | pending |

## Cost controls

- Cheap preflight gate so quiet backlogs cost ~nothing.
- Per-fire cap bounds new PRs (and downstream CR loops) per run.
- The `schedule` API floor is **1 hour** (`*/30` is rejected). Frequency x cap is
  the spend lever.

## Operating the routine

- Manage via the `schedule` skill (`RemoteTrigger`: list/get/create/update/run).
  You **cannot delete** via API; use https://claude.ai/code/routines.
- **Always test first**: create disabled, do one `run`, confirm the cloud env can
  clone + implement + open a PR + edit labels, then `enable`.
- **Kill switch**: update `{enabled:false}` or toggle in the routines UI.
- Environment: Default (`anthropic_cloud`). Model: `claude-sonnet-4-6`.

## Known runtime quirks (observed)

- The CCR runtime auto-appends a `Generated by Claude Code` / claude.ai session
  footer to PR bodies. This violates the no-Claude-mention rule, so the routine
  strips it post-create (Phase 2). If it re-appears after edit, disable it at the
  environment level.
- Untracked files under a developer's `~/.claude` (which is the `dotclaude`
  checkout) get wiped by sync. Commit anything that must persist (this file is an
  example).
