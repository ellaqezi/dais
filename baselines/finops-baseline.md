# DAIS FinOps Baseline
# Prepended to every agent prompt alongside shared-baseline.md and gdpr-baseline.md.
# STABLE LAYER — governs token budget, cost routing, and FinOps discipline across ALL agents.
# Principle A3, D3: cost routing is structural and declared in shared files.

---

## FinOps Rules (All Agents)

### Routing Decision Block

Every agent call must be preceded by a `[ROUTING-DECISION]` block.
Format is defined in `data/complexity-router.md`.
Missing routing decision blocks are rejected by the post-execution reviewer.

### Tier Compliance

1. Operate at the tier declared in `system.config.yaml` for this agent.
2. If the task is **simpler** than the declared tier: complete it at the declared tier.
   Optionally emit a `[COMPLEXITY-DOWNGRADE-NOTE: task fits <lower tier> — running at declared <tier> per config]`.
3. If the task is **more complex** than the declared tier: halt and emit:
   ```
   [COMPLEXITY-UPGRADE-NEEDED: current=<tier> recommended=<tier> reason=<one sentence>]
   ```
   Do NOT attempt a task at a tier that cannot handle it reliably.
4. Agents with `dynamic_routing: false` in `system.config.yaml` must never self-downgrade.
   This constraint is enforced by the pre-execution validator.

### Output Scope Discipline

- Do not pad outputs to reach `min_lines`. Padding is waste.
- Do not truncate outputs below structural completeness to meet `max_lines`.
  If projected output will exceed `max_lines`, emit:
  ```
  [SCOPE-WARNING: projected <n> lines, max <max> — proceeding; manifest-agent will flag for review]
  ```
- Every section declared in the agent's six-pillar structure must be complete.
  A section that is 60% complete is worse than an explicit gap.

### Cost Metadata (Development / Staging)

In non-production environments, every output includes cost metadata in the footer:

```
[tokens-in: <n>] [tokens-out: <n>] [cost-usd: <float>] [tier: <tier>] [workflow: <id>]
```

In production environments, this block is suppressed unless `debug_mode: true` is set in session config.

### Session FinOps Summary

At end of every session, the finops-agent emits:

```
[FINOPS-SUMMARY]
total-agents-run:       <n>
tier-distribution:      low=<n> mid=<n> high=<n>
forced-high-agents:     <list>
estimated-cost-usd:     <float>
savings-vs-all-high:    <float> USD (estimated)
high-tier-unjustified:  <n> (agents classified high without forced=yes)
```

If `high-tier-unjustified > 0`, emit:
```
[FINOPS-ALERT: <n> agent(s) ran at HIGH tier without forced routing — review complexity classifications]
```

### FinOps Discipline Principle

The goal is to match model capability to task need. Using HIGH for tasks that fit MID
is not "safe" — it is waste that degrades cost predictability and erodes team trust
in the system's FinOps controls. The complexity router exists to prevent this.
