# DAIS — Agent Inventory
# Machine-readable index of all agents in the system.
# VARIABLE LAYER — add a new entry here when a new agent is added. (A5)
# Do NOT modify stable-layer files (system.config.yaml shared structure) to accommodate a new agent.
# Adding an agent: (1) new file in agents/ following six-pillar structure, (2) entry here, (3) entry in system.config.yaml agents block.

---

## System Overview

DAIS (DevEx Augmentation and Insight System) is a production-grade, multi-agent project harness
for bootstrapping new software projects and auditing existing ones.

**Consumers**: Software engineers and architects bootstrapping or auditing projects.
**Compliance regime**: GDPR (default). Override per session via manifest.
**FinOps**: Dynamic cost-tier routing via `data/complexity-router.md`. Forced-HIGH agents declared explicitly.

---

## Agent Inventory

### Phase 1 — DERIVE

| Agent | File | Mode | Tier | Dynamic Routing |
|-------|------|------|------|----------------|
| derive-agent | [agents/phase-1/derive-agent.md](agents/phase-1/derive-agent.md) | both | mid | yes |

**derive-agent** — Derives project topology, stack, PII fields, and DPIA triggers from existing
artefacts. Produces the context object consumed by manifest-agent. Does not ask the engineer
for information derivable from artefacts. (Principle B1, B2)

---

### Phase 2 — MANIFEST

| Agent | File | Mode | Tier | Dynamic Routing |
|-------|------|------|------|----------------|
| manifest-agent | [agents/phase-2/manifest-agent.md](agents/phase-2/manifest-agent.md) | both | low | no (fixed) |

**manifest-agent** — Transforms the derived context into a human-readable generation plan.
Gates Phase 3 on explicit `CONFIRM`. Shows every file, every agent, every forced-HIGH flag,
and the compliance baseline before a single artefact is generated. (Principle D2)

---

### Phase 3 — EXECUTE (Bootstrap mode)

| Agent | File | Mode | Tier | Dynamic Routing | Forced-HIGH |
|-------|------|------|------|----------------|-------------|
| scaffold-agent | [agents/phase-3/bootstrap/scaffold-agent.md](agents/phase-3/bootstrap/scaffold-agent.md) | bootstrap | mid | yes | no |
| architecture-agent | [agents/phase-3/bootstrap/architecture-agent.md](agents/phase-3/bootstrap/architecture-agent.md) | bootstrap | high | yes | no |
| ci-cd-agent | [agents/phase-3/bootstrap/ci-cd-agent.md](agents/phase-3/bootstrap/ci-cd-agent.md) | bootstrap | mid | yes | no |
| security-agent | [agents/phase-3/bootstrap/security-agent.md](agents/phase-3/bootstrap/security-agent.md) | both | **HIGH** | **no** | **YES ⚠** |
| observability-agent | [agents/phase-3/bootstrap/observability-agent.md](agents/phase-3/bootstrap/observability-agent.md) | bootstrap | mid | yes | no |
| testing-agent | [agents/phase-3/bootstrap/testing-agent.md](agents/phase-3/bootstrap/testing-agent.md) | bootstrap | mid | yes | no |
| docs-agent | [agents/phase-3/bootstrap/docs-agent.md](agents/phase-3/bootstrap/docs-agent.md) | bootstrap | low | yes | no |
| finops-agent | [agents/phase-3/bootstrap/finops-agent.md](agents/phase-3/bootstrap/finops-agent.md) | bootstrap | mid | yes | no |

**⚠ security-agent is a Forced-HIGH agent.** Tier cannot be downgraded. Cannot be excluded from the manifest.
Declaration: `system.config.yaml → agents.security-agent.dynamic_routing: false, forced_high: true`.

---

### Phase 3 — EXECUTE (Audit mode)

| Agent | File | Mode | Tier | Dynamic Routing |
|-------|------|------|------|----------------|
| audit-agent | [agents/phase-3/audit/audit-agent.md](agents/phase-3/audit/audit-agent.md) | audit | high | yes |
| gap-agent | [agents/phase-3/audit/gap-agent.md](agents/phase-3/audit/gap-agent.md) | audit | mid | yes |
| remediation-agent | [agents/phase-3/audit/remediation-agent.md](agents/phase-3/audit/remediation-agent.md) | audit | mid | yes |

Audit agents run **sequentially**: audit-agent → gap-agent → remediation-agent.
Each agent's output is the next agent's input (handoff schemas in `validators/handoff-schemas/`).

---

### Cross-Cutting

| Agent | File | Mode | Tier | Dynamic Routing |
|-------|------|------|------|----------------|
| post-execution-reviewer | [validators/post-execution-reviewer.md](validators/post-execution-reviewer.md) | both | mid | no (fixed) |

**post-execution-reviewer** — Separate model instance. Evaluates every agent output for structural
compliance. Issues `ACCEPT` or `REJECT` verdicts with quoted evidence. Never rewrites. (Principle D5)

---

## Extension Protocol (Principle A5)

To add a new agent without modifying stable-layer files:

1. Create `agents/<phase>/<mode>/<new-agent-id>.md` following the six-pillar structure (A4).
2. Validate with: `python validators/pre-execution-validator.py agents/.../<new-agent-id>.md`
3. Add entry to `system.config.yaml` under `agents:` with tier, dynamic_routing, min_lines, max_lines.
4. Add entry to `scope-manifests.yaml` under the appropriate scope's `phase_order.agents` list.
5. Add entry to this file (AGENTS.md) in the relevant phase section.

**Zero stable-layer files should be modified.** If you find yourself editing anything other than
the four files above, stop and flag: `[DESIGN CONFLICT — A5]`.

---

## Data Files

| File | Purpose | Consulted by |
|------|---------|-------------|
| [data/pii-classifier.yaml](data/pii-classifier.yaml) | PII field patterns and actions | derive-agent, security-agent, audit-agent, post-execution-reviewer |
| [data/dpia-triggers.yaml](data/dpia-triggers.yaml) | DPIA requirement triggers | derive-agent, security-agent, audit-agent |
| [data/severity-rubric.yaml](data/severity-rubric.yaml) | Severity level definitions | audit-agent, gap-agent, security-agent |
| [data/dark-patterns.yaml](data/dark-patterns.yaml) | UX/consent dark patterns | security-agent, audit-agent, scaffold-agent |
| [data/trigger-keywords.yaml](data/trigger-keywords.yaml) | Forced routing triggers | orchestrator (before every agent call) |
| [data/complexity-router.md](data/complexity-router.md) | Tier classification heuristics | orchestrator (routing decisions) |

---

## Shared Baselines

| File | Purpose | Applied to |
|------|---------|-----------|
| [baselines/shared-baseline.md](baselines/shared-baseline.md) | Universal output constraints | All agents |
| [baselines/gdpr-baseline.md](baselines/gdpr-baseline.md) | GDPR compliance rules | All agents |
| [baselines/finops-baseline.md](baselines/finops-baseline.md) | Token budget and cost routing rules | All agents |

---

## Validators

| File | Purpose | Run when |
|------|---------|---------|
| [validators/pre-execution-validator.py](validators/pre-execution-validator.py) | Structural validation (six-pillar schema, frontmatter, placeholders) | Before every agent is used in the pipeline |
| [validators/post-execution-reviewer.md](validators/post-execution-reviewer.md) | Output compliance review | After every agent produces output |

Handoff schemas: [validators/handoff-schemas/](validators/handoff-schemas/)

---

## Design Conflict Flag Format

Any proposed change that violates a system principle must be flagged before implementation:

```
[DESIGN CONFLICT — <group><number>]
Proposed change: <description>
Conflict: <how it violates the principle>
Alternative: <how to achieve the goal without the violation>
```
