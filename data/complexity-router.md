# DAIS Complexity Router
# Heuristics for classifying task complexity and assigning model tiers.
# Invoked before every agent execution (except forced-HIGH agents).
# Principle D3: match tier to task complexity, not role label.
# Principle FinOps: classify first; do not default to HIGH without justification.

---

## Tier Definitions

| Tier | Model class | Token budget (relative) | Use when |
|------|-------------|------------------------|----------|
| low  | Small/fast (e.g., GPT-4o-mini, Claude Haiku) | 1x | Single-file formatting, template fill, classification, lookup |
| mid  | Balanced (e.g., GPT-4o, Claude Sonnet) | 3x | Standard generation, docs, structured output, 2–5 input synthesis |
| high | Capable (e.g., GPT-4o, Claude Opus) | 8x | Multi-step reasoning, architecture, cross-file analysis, security |

---

## Classification Heuristics

### → low tier
- Input is fully structured (fill a YAML template from known values)
- Output is a single artefact with no cross-file dependencies
- No reasoning chain required — transformation is essentially 1:1
- Output length < 80 lines
- No compliance implications
- Routing decision itself requires no judgment

**Examples**: manifest-agent (formatting derived context), docs-agent template fill,
gap-register severity label lookup

### → mid tier (default when uncertain)
- Output requires synthesis of 2–5 inputs
- Standard code generation from a clear, fully-specified input
- Documentation generated from existing structured content
- Output length 80–200 lines
- Compliance implications that need flagging but not deep analysis

**Examples**: scaffold-agent (standard stack), ci-cd-agent (known CI platform),
testing-agent (standard coverage config), finops-agent (routing config)

### → high tier
- Output requires reasoning across 5+ inputs or significant implicit context
- Architecture decisions with downstream structural consequences
- Cross-file analysis (detecting patterns across a codebase)
- Output length > 200 lines
- Security, privacy, or legal implications requiring expert reasoning
- Two different model instances running this prompt might produce structurally different outputs
- Threat modelling, adversarial thinking, compliance gap analysis

**Examples**: architecture-agent, security-agent, audit-agent (complex codebase),
any task matching `security` or `gdpr_pii` triggers in trigger-keywords.yaml

---

## Forced-HIGH Overrides (non-negotiable, declared in system.config.yaml)

These assignments ignore all heuristics above. The router emits the routing decision
but marks `forced: yes` and does NOT reclassify:

| Agent | Config flag | Reason |
|-------|------------|--------|
| security-agent | `dynamic_routing: false` | Safety-critical; downgrade risks missed vulnerabilities |
| Any task matching `security` trigger | `override_dynamic_routing: true` | Attack surface analysis is always HIGH |
| Any task matching `gdpr_pii` trigger | `override_dynamic_routing: true` | GDPR violations are always HIGH minimum |

---

## Router Output Format

Emit this block immediately before every routed agent call.
Missing blocks are rejected by the post-execution reviewer.

```
[ROUTING-DECISION]
agent:           <agent-id>
requested-tier:  <low|mid|high>
classified-tier: <low|mid|high>
reasoning:       <one sentence explaining classification>
fallback-tier:   <tier if primary model unavailable>
forced:          <yes|no>
cost-multiplier: <1x|3x|8x>
```

---

## Cost Discipline Rules

1. Classify before routing. Never default to HIGH without a written justification in the routing decision.
2. A routing-decision block is mandatory for every agent call. Missing blocks fail the post-execution review.
3. If the classified tier conflicts with `system.config.yaml`, the config wins. The router documents the conflict:
   `[ROUTING-CONFLICT: classified=<tier>, config=<tier>, config wins — reason: <config rationale>]`
4. All routing decisions are logged. The finops-agent aggregates them into a session FinOps summary.
5. Forced-HIGH agents cannot be downgraded. If the model at HIGH tier is unavailable, halt and escalate to human.

---

## FinOps Guardrails

- Do not run HIGH-tier agents for tasks that provably fit mid criteria.
- After every session, the finops-agent reports: `tier-distribution`, `estimated-cost-usd`,
  `savings-vs-all-high-usd`, `forced-high-agents`.
- If >50% of agent calls are classified HIGH without `forced: yes`, surface a
  `[FINOPS-ALERT: high-tier overuse — review complexity classifications]` in the finops summary.
