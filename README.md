# DAIS — DevEx Augmentation and Insight System

> A production-grade, multi-agent project harness for bootstrapping new software projects
> and auditing existing ones. Built on 13 structural design principles. GDPR-compliant by default.
> FinOps-aware by design.

---

## What DAIS Does

| Mode | Input | Output |
|------|-------|--------|
| **bootstrap** | Empty or bare project directory | Production-ready project skeleton with CI/CD, security baseline, observability, tests, and docs |
| **audit** | Existing codebase | Prioritised gap register + sprint-ready remediation plan |

---

## How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 1 — DERIVE                                                │
│  derive-agent scans the repo and builds a typed context object.  │
│  No questions asked. Facts only.                                 │
└────────────────────────────┬─────────────────────────────────────┘
                             │ context object
┌────────────────────────────▼─────────────────────────────────────┐
│  PHASE 2 — MANIFEST                                              │
│  manifest-agent presents the full generation plan:               │
│    • every file to be generated                                  │
│    • every agent, tier, routing mode                             │
│    • compliance baseline applied                                 │
│    • forced-HIGH agents flagged                                  │
│    • any detected gaps                                           │
│  ───────────────────────────────────────────────────             │
│  Human replies: CONFIRM | CORRECT: | EXCLUDE: | ABORT            │
└────────────────────────────┬─────────────────────────────────────┘
                             │ confirmed manifest
┌────────────────────────────▼─────────────────────────────────────┐
│  PHASE 3 — EXECUTE                                               │
│  Bootstrap: scaffold → architecture → [ci-cd, observability,     │
│             testing, docs, finops] (parallel) → security-agent   │
│  Audit:     audit-agent → gap-agent → remediation-agent          │
│             (sequential, handoff-validated)                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Bootstrap a new project

```
System prompt: [baselines/shared-baseline.md] + [baselines/gdpr-baseline.md] + [baselines/finops-baseline.md]

User input:
  "Design a multi-agent project harness for [domain]
   serving [consumer]
   under [compliance]
   for a [team type] team."
```

Or more concretely:

```
User input:
  "Bootstrap a new TypeScript/Express REST API for a platform team.
   GDPR applies. GitHub Actions CI."
```

DAIS will run Phase 1 (DERIVE) automatically, present a Phase 2 manifest, and await `CONFIRM`.

### Audit an existing project

```
User input:
  "Audit this project for production-readiness gaps."
  [provide project root or paste key files]
```

---

## Principles Applied

This system is built on the [AI Agent System Design Meta-Principles](meta-principles.md) (13 principles).

| Principle | Where it manifests in DAIS |
|-----------|--------------------------|
| A1 — Separate by Rate of Change | Stable layer: baselines/, validators/. Variable: scope-manifests.yaml. Session: project root, overrides. |
| A2 — Single Responsibility Per Agent | Every agent has one named noun specialisation. See AGENTS.md. |
| A3 — Separate Policy from Execution | Shared rules in baselines/. Data-file lookups, not inline instructions. |
| A4 — Six-Pillar Agent Structure | All agent prompts: Role / Objective / Community / Key Points / Shape / Constraints |
| A5 — Extend Without Rewriting | New agent = new file + 3 manifest entries. Zero stable-layer edits. |
| B1 — Evidence Over Self-Report | derive-agent reads artefacts. Never asks what the config already declares. |
| B2 — Absorb Friction at System Layer | Phase 1 does all prep. Human confirms; doesn't prepare. |
| B3 — Degrade Gracefully and Explicitly | [GAP-n] format with required-by and reason. HALT-level gaps block pipeline. |
| C1 — Compliance Is Architecture | PII, DPIA, severity, dark patterns all in data files. Checked at entry. |
| C2 — Forced Routing | security-agent: forced-HIGH, dynamic_routing: false. Keyword triggers in data/trigger-keywords.yaml. |
| C3 — Resolve Decisions Upstream | All routing, severity, PII resolved in data files before execution. |
| D2 — Gate Irreversible Steps | Phase 2 manifest shows complete plan. CONFIRM required before Phase 3. |
| D3 — Dynamic Cost-Tier Routing | Complexity router classifies tasks. Tier-per-agent in system.config.yaml. FinOps summary per session. |
| D4 — Auditability by Default | Metadata footer required on every output. Missing footer = REJECT. |
| D5 — Quality Is Tested, Not Self-Certified | pre-execution-validator.py (exit code). post-execution-reviewer.md (separate instance, ACCEPT/REJECT). |

---

## File Structure

```
dais/
├── system.config.yaml                    ← Master manifest. Agent tiers, FinOps config.
├── scope-manifests.yaml                  ← Execution order by mode (bootstrap/audit).
├── AGENTS.md                             ← Agent inventory and extension protocol.
├── README.md                             ← This file.
│
├── data/                                 ← Authoritative reference data. Agents look up; never self-assess.
│   ├── pii-classifier.yaml
│   ├── dpia-triggers.yaml
│   ├── severity-rubric.yaml
│   ├── dark-patterns.yaml
│   ├── trigger-keywords.yaml
│   └── complexity-router.md
│
├── baselines/                            ← Prepended to every agent. Stable layer.
│   ├── shared-baseline.md
│   ├── gdpr-baseline.md
│   └── finops-baseline.md
│
├── agents/
│   ├── phase-1/
│   │   └── derive-agent.md
│   ├── phase-2/
│   │   └── manifest-agent.md
│   └── phase-3/
│       ├── bootstrap/
│       │   ├── scaffold-agent.md
│       │   ├── architecture-agent.md
│       │   ├── ci-cd-agent.md
│       │   ├── security-agent.md          ← Forced-HIGH ⚠
│       │   ├── observability-agent.md
│       │   ├── testing-agent.md
│       │   ├── docs-agent.md
│       │   └── finops-agent.md
│       └── audit/
│           ├── audit-agent.md
│           ├── gap-agent.md
│           └── remediation-agent.md
│
└── validators/
    ├── pre-execution-validator.py         ← Blocks invalid agents (exit code 1).
    ├── post-execution-reviewer.md         ← Separate instance. ACCEPT / REJECT verdicts.
    └── handoff-schemas/
        ├── derive-to-manifest.schema.yaml
        ├── manifest-to-execute.schema.yaml
        └── audit-to-gap.schema.yaml
```

---

## Validation

Run the pre-execution validator against any agent before using it:

```bash
python validators/pre-execution-validator.py agents/phase-1/derive-agent.md system.config.yaml
```

Exit code 0 = valid. Exit code 1 = blocked with error list.

---

## Extending DAIS

See the **Extension Protocol** in [AGENTS.md](AGENTS.md).

Rule: adding a new agent requires zero modifications to stable-layer files.
If you find yourself editing `baselines/`, `validators/pre-execution-validator.py`, or
the stable structure of `system.config.yaml`, stop and raise a `[DESIGN CONFLICT — A5]`.

---

## Design Conflict Flags

Any proposed change that violates a system principle must be flagged:

```
[DESIGN CONFLICT — <group><number>]
Proposed change: <description>
Conflict: <how it violates the principle>
Alternative: <how to achieve the goal without the violation>
```

Do not resolve design conflicts silently.
