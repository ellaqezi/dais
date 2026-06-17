# devexnet — Agent and Command Inventory

This file serves two roles:
- **DAIS**: declares the agents used to bootstrap and audit this project.
- **loom-reed-light**: maps developer command phrases to workflow prompts.

---

## loom-reed-light Workflow Commands

Use these command phrases with Claude Code to invoke the workflow prompts.

| Command | Prompt | Tier | Purpose |
|---------|--------|------|---------|
| `init light workspace` | [`prompts/init.md`](prompts/init.md) | Haiku | Create or migrate into spec/ + tasks/ layout |
| `add a spec for <topic>` | [`prompts/add-spec.md`](prompts/add-spec.md) | Sonnet | Author spec/<topic>.md before planning |
| `plan next work` | [`prompts/plan.md`](prompts/plan.md) | Sonnet | Translate spec changes into backlog tasks |
| `refine task <id>` | [`prompts/refine.md`](prompts/refine.md) | Sonnet | Decompose needs-refine tasks into S/M with acceptance criteria |
| `implement task <id>` | [`prompts/implement.md`](prompts/implement.md) | Sonnet | Code, tests, and docs for a specific S/M task |
| `plan refactors` | [`prompts/refactor.md`](prompts/refactor.md) | Opus | Structural improvement tasks aligned to specs |
| `stabilize scope <name>` | [`prompts/stabilize.md`](prompts/stabilize.md) | Sonnet | Resilience and stabilization tasks for recent features |
| `cleanup after <feature/spec>` | [`prompts/cleanup.md`](prompts/cleanup.md) | Haiku | Schedule cleanup tasks retiring drift and outdated artifacts |

Tier column maps to dotclaude model tier vocabulary: Haiku (low-judgment), Sonnet (mid), Opus (high-judgment, architectural).
Full tier rationale in `docs/finops/token-routing-strategy.md`.

---

## DAIS Agent Inventory

These agents were used to bootstrap this project. Re-run DAIS audit sequence periodically
to detect architectural drift.

### Phase 1 — DERIVE

| Agent | File | Tier | Purpose |
|-------|------|------|---------|
| derive-agent | `agents/phase-1/derive-agent.md` | mid | Extracts topology, stack, PII fields, DPIA triggers from existing artefacts |

### Phase 2 — MANIFEST

| Agent | File | Tier | Purpose |
|-------|------|------|---------|
| manifest-agent | `agents/phase-2/manifest-agent.md` | low | Gates Phase 3 on explicit CONFIRM |

### Phase 3 — Bootstrap

| Agent | File | Tier | Forced-HIGH |
|-------|------|------|-------------|
| scaffold-agent | `agents/phase-3/bootstrap/scaffold-agent.md` | mid | no |
| architecture-agent | `agents/phase-3/bootstrap/architecture-agent.md` | high | no |
| ci-cd-agent | `agents/phase-3/bootstrap/ci-cd-agent.md` | mid | no |
| security-agent | `agents/phase-3/bootstrap/security-agent.md` | **HIGH** | **YES** |
| observability-agent | `agents/phase-3/bootstrap/observability-agent.md` | mid | no |
| testing-agent | `agents/phase-3/bootstrap/testing-agent.md` | mid | no |
| docs-agent | `agents/phase-3/bootstrap/docs-agent.md` | low | no |
| finops-agent | `agents/phase-3/bootstrap/finops-agent.md` | mid | no |

### Phase 3 — Audit (run periodically)

| Agent | File | Tier | Run order |
|-------|------|------|-----------|
| audit-agent | `agents/phase-3/audit/audit-agent.md` | high | 1 |
| gap-agent | `agents/phase-3/audit/gap-agent.md` | mid | 2 |
| remediation-agent | `agents/phase-3/audit/remediation-agent.md` | mid | 3 |

### Cross-Cutting

| Agent | File | Tier | Notes |
|-------|------|------|-------|
| post-execution-reviewer | `validators/post-execution-reviewer.md` | mid | Separate model instance; ACCEPT/REJECT only |

---

## Extension Protocol

To add a new loom-reed-light command: add a prompt file to `prompts/` and update the
command table above. Keep command phrases consistent with the existing vocabulary.

To run DAIS audit against this project:
```bash
# From the DAIS root:
# Phase 1: derive-agent scans tests/bootstrap/devexnet/
# Phase 2: manifest-agent presents gap register
# Phase 3: audit-agent → gap-agent → remediation-agent
```
