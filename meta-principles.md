# AI Agent System Design — Reusable Meta-Principles Prompt

---

## WHAT THIS PROMPT IS

These principles were extracted from building a production-grade, multi-agent
SDLC system. They are stated in domain-neutral form. They apply wherever a
system must decompose work across specialized agents, route inputs reliably,
enforce constraints structurally, and produce outputs a human can verify and
trust.

They are not a template. They are a constraint set. Principles take precedence
over any specific pattern derived from them.

---

## THE THIRTEEN PRINCIPLES

Grouped by concern. Apply all thirteen. No principle is optional.

---

### GROUP A — STRUCTURE
*How the system and its components are organized.*

---

#### A1 — Separate by Rate of Change
Decompose any system into layers defined by how often each layer changes —
not by what each layer does.

| Layer | Changes when | Examples |
|-------|-------------|---------|
| Stable | Never (between users, sessions, or topology changes) | Six-pillar structure, validation rules, metadata footer format |
| Variable | Team type or context changes | Topology-specific principles, compliance regime, agent inventory |
| Session | Every run | Project root, user overrides, runtime inputs |

**Test**: Can the variable layer be swapped without touching the stable layer?
If not, the layers are entangled. Separate them.

**Flag**: `[DESIGN CONFLICT — A1]` if a new topology requires editing the
stable layer.

---

#### A2 — Single Responsibility Per Agent
Every agent has exactly one named specialization. If an agent serves two
audiences or produces two fundamentally different artifact types, split it.

**Test**: Complete this sentence with one noun: *"This agent is the ___ agent."*
If the noun requires a conjunction (e.g., "design and review"), split the agent.

---

#### A3 — Separate Policy from Execution (DRY Baselines)
Shared rules live in shared baseline files prepended to every agent.
Agent-specific prompts contain only role-specific logic.

**Rule**: If a constraint appears in more than one agent prompt, it belongs in
a shared baseline. Every duplication is a future inconsistency.

**Corollary**: Agents do not decide shared concerns (what is PII, what severity
a finding is, what triggers a DPIA). They look those up from versioned data
files. Judgment criteria are data, not instructions.

---

#### A4 — Six-Pillar Agent Structure (Mandatory)
Every agent prompt contains these sections in this exact order:

1. **Role** — Identity and single named expertise
2. **Objective** — The one outcome this agent produces
3. **Community/Audience** — Primary and secondary consumers; tone per consumer
4. **Key Points** — Quality bars, domain-specific guidelines, data file references
5. **Shape** — Output format, required artifacts, structural constraints
6. **Constraints & Behavior** — Refusal patterns, scope boundaries, defaults,
   complexity self-reporting, redirect targets for out-of-scope requests

Plus YAML frontmatter (schema-validated before execution).

---

#### A5 — Extend Without Rewriting
A well-designed system accommodates new cases by extension, not by modification
of stable components.

**Test**: Add one new agent or one new compliance regime. How many existing
files must be modified?

The answer must be: **zero stable-layer files**.

New agents are expressed as:
- One new file following the six-pillar structure
- One new entry in the system manifest (`system.config.yaml`)
- One new scope entry in `scope-manifests.yaml`

**Flag**: `[DESIGN CONFLICT — A5]` if adding a new case requires editing a
stable-layer file.

---

### GROUP B — INPUT HANDLING
*How the system receives and processes what humans provide.*

---

#### B1 — Evidence Over Self-Report
When the system needs to model a human's context, preferences, or situation:
prefer evidence extracted from existing artefacts over answers to questions
about themselves.

Self-description is aspiration. Artefacts are evidence.

**Test**: For every input field — could this be derived from something the
human has already made? If yes, derive it. Ask only for what has no
artefact trace.

**In this system**: Topology, compliance regime, team size, and agent inventory
are all derivable from `system.config.yaml`. The system reads the config;
it does not ask the human to re-describe what the config already declares.

---

#### B2 — Absorb Friction at the System Layer
Every step the human must perform before the system can proceed is a
candidate for absorption. The human's job is judgment and confirmation —
not preparation, cleaning, categorisation, or formatting.

**Test**: Before a user gets value, what do they have to do first?
Each of those steps is friction. Move it inside the system.

**In this system**: Phase 1 (DERIVE) does all preparation automatically.
Phase 2 (MANIFEST) shows the result. The human confirms or corrects.
The human does not prepare the manifest.

---

#### B3 — Degrade Gracefully and Explicitly
When the system receives partial inputs, it must produce partial but usable
outputs — and name its gaps explicitly.

Silent failure is never acceptable.
Silent gap-filling is also never acceptable.

**Test**: Run the system with 50% of expected inputs missing. Does it fail?
Does it fill gaps silently? Either answer is wrong. It should produce a
partial output with clearly labelled gaps.

**In this system**: Phase 1 halts with a named `[GAP-n]` list when
prerequisites are missing. It does not proceed. It does not assume missing
files are unnecessary.

**Gap format**:
```
[GAP-01] <file> — required by: <consumer> (<reason>)
```

---

### GROUP C — CONSTRAINTS & COMPLIANCE
*How the system enforces rules it must not violate.*

---

#### C1 — Compliance Is Architecture, Not Cleanup
Any constraint that matters — privacy, security, quality, legal — must be
enforced at the point of entry, not remediated after the fact.

**Test**: If you removed all human review from your compliance process, what
would slip through? Everything that would slip through is a structural gap,
not a process gap.

**In this system**:
- PII detection: `pii-classifier.yaml` (checked before processing — not after)
- GDPR triggers: `dpia-triggers.yaml` (consulted by agents — not self-assessed)
- Dark patterns: `dark-patterns.yaml` (lookup table — not agent judgment)
- Severity criteria: `severity-rubric.yaml` (explicit criteria — not inferred)
- Structural validation: `pre-execution-validator.py` (exit code — not prose)

Compliance is expressed as data files agents consult and validators that
block non-compliant outputs. It is not expressed as instructions agents
may or may not follow.

---

#### C2 — Forced Routing for Non-Negotiable Concerns
Some routing decisions are not optional and cannot be downgraded for cost.

| Trigger source | Routing action |
|----------------|---------------|
| Keyword match in `trigger-keywords.yaml` | Route as declared in file |
| `dynamic_routing: false` in agent config | Always run at declared tier |
| PII field match in `pii-classifier.yaml` | Force route to security agent |
| Handoff schema validation failure | Block; return missing fields |

These are structural constraints declared in data files.
The orchestrator matches against them; it does not interpret them.

---

#### C3 — Resolve Decisions Upstream
Every ambiguous decision that could be made at the planning layer must be
made there. The execution layer receives fully specified instructions.
If the execution layer must make a judgment call, the planning layer
has failed.

**Test**: If two different model instances received this instruction, would
they produce structurally identical outputs? If not, there is an unresolved
decision in the instruction.

**In this system**: Routing criteria, severity levels, PII definitions, scope
boundaries, and DPIA triggers are all resolved in data files before any agent
executes. Agents look up; they do not decide.

---

### GROUP D — EXECUTION & VERIFICATION
*How outputs are produced and validated.*

---

#### D1 — Opinionated Defaults with Documented Rationale
Every default is:
- Applied automatically (no silent assumptions)
- Declared in `system.config.yaml` with a one-line rationale
- Overridable via session input (each override confirmed in the manifest)
- Never re-asked if derivable from existing configuration

**Anti-pattern**: Asking the human to choose between options that industry
best practice has already resolved.

---

#### D2 — Gate Irreversible Steps
Any step that cannot be easily undone — generating 30 files, committing
infrastructure, sending communications — requires explicit human confirmation
immediately before execution.

Confirmation must surface the system's interpretation in verifiable terms —
not just ask yes/no.

**Test**: Read the confirmation your system shows before an irreversible step.
Could a human tell from that confirmation exactly what is about to happen
and whether it matches their intent? If not, the gate is insufficient.

**In this system**: Phase 2 (MANIFEST) shows the complete generation plan —
file list, agent ids, tier assignments, compliance baseline, forced-HIGH
agents — before a single file is generated. The human confirms the manifest,
not a topology label.

**Manifest must include**:
- Every file that will be generated (path + purpose)
- Every agent (id, tier, routing mode, SLO impact)
- Compliance baseline applied
- Forced-HIGH agents explicitly flagged
- Exact reply options (`CONFIRM`, `CORRECT: <field> <value>`, `EXCLUDE:`, `ABORT`)

---

#### D3 — Dynamic Cost-Tier Routing
Match model tier to task complexity, not to role label.

| Complexity signal | Default tier |
|------------------|-------------|
| Classification, templates, single-file formatting | Low |
| Standard generation, documentation, structured output | Mid |
| Multi-step reasoning, architecture, cross-file analysis | High |
| Safety-critical (security, incident response) | High — forced, no downgrade |

Tier decisions are declared in `system.config.yaml` per agent.
The complexity router classifies tasks against heuristics in
`complexity-router.md` and emits a structured routing decision with
`reasoning` and `fallback_tier`.

Always document in output metadata: `[complexity: low|mid|high]`

---

#### D4 — Auditability by Default
Every agent output ends with a metadata footer. This is a structural
requirement, not a suggestion. Outputs missing the footer are rejected
by the post-execution reviewer.

```
---
[agent: <id>] [complexity: low|mid|high] [gdpr-touched: yes|no] [consumer-impact: single-team|multi-team|platform-wide]
```

In development/staging environments, extend with cost data:
```
[tokens-in: <n>] [tokens-out: <n>] [cost-usd: <float>] [tier: <tier>] [workflow: <id>]
```

---

#### D5 — Quality Is Tested, Not Self-Certified
Quality requirements are expressed as structural tests with pass/fail
conditions. They are run by a separate validator — not by the generating
model against its own output.

**Violation in v1.0**: "Quality Bar Is Self-Verifiable" — the generating
model ran a checklist against its own output. This is circular and fails
silently when the model is wrong about its own output.

**Correct pattern**:
- Pre-execution: `validators/pre-execution-validator.py` — checks structure
  before the prompt is used. Exit code 1 = invalid. Blocks pipeline.
- Post-execution: `validators/post-execution-reviewer.md` — a separate
  model instance checks output structure. Verdict: `ACCEPT` or `REJECT`
  with quoted evidence. The reviewer never rewrites; only judges.

**Every quality test must satisfy**:
Can it be evaluated without the evaluator knowing what the "right answer"
is supposed to feel like? If aesthetic judgment is required, it is not
yet a testable requirement.

| Test | Pass condition (machine-evaluable) |
|------|-----------------------------------|
| Six sections present | `grep -c "^## Role\|^## Objective\|^## Community\|^## Key Points\|^## Shape\|^## Constraints"` = 6 |
| Metadata footer present | Last non-empty line matches `\[agent:.*\]\s\[complexity:.*\]\s\[gdpr-touched:.*\]` |
| No PII in output | Zero matches against `pii-classifier.yaml` patterns |
| Refusal pattern present | Body contains `refuse\|will not\|cannot` with a condition clause |
| Few-Shot Example present | Body contains `**Input**:` and `**Output**:` block |
| No placeholder text | Zero matches for `<TODO>\|TBD\|\[fill in\]` |
| Line count in range | `wc -l` within `[min_lines, max_lines]` from agent config |

---

## DESIGN CONFLICT FLAG FORMAT

Any proposed change that violates one of the principles above must be flagged
before implementation. Do not resolve design conflicts silently.

```
[DESIGN CONFLICT — <group><number>]
Proposed change: <description>
Conflict: <how it violates the principle>
Alternative: <how to achieve the goal without the violation>
```

---

## APPLICATION PATTERN

When asked to design a new agent system in any domain:

**Before designing anything, answer:**

| Question | Principle |
|----------|-----------|
| What never changes? What changes per context? What changes per run? | A1 |
| What can be derived from existing artefacts vs. must be asked? | B1 |
| What preparation does the human currently do that the system could absorb? | B2 |
| What happens when inputs are incomplete? Name the gaps explicitly. | B3 |
| Which constraints must be enforced at entry? Which data files express them? | C1 |
| Which routing decisions are non-negotiable? What data file governs each? | C2 |
| Which decisions must be resolved before execution begins? | C3 |
| What are the irreversible steps? What does the confirmation gate show? | D2 |
| When a new agent or format is added, how many stable files are modified? | A5 |
| Can every quality requirement produce a pass/fail without aesthetic judgment? | D5 |

**Then proceed in this order:**

1. Define the three layers (stable / variable / session) — A1
2. Define the six-pillar structure for this domain — A4
3. Extract shared policies into baseline files — A3
4. Define judgment criteria as data files (not inline instructions) — C1, C3
5. Define the agent inventory in a machine-readable manifest — A5
6. Set tier defaults and forced-routing rules in config — D3, C2
7. Define handoff schemas for sequential agent pairs — B3
8. Build pre-execution validator against six-pillar schema — D5
9. Build post-execution reviewer as a separate model instance — D5
10. Design Phase 2 manifest so the human confirms plan, not label — D2
11. Generate files in dependency order (data files → baselines → agents → AGENTS.md) — A3
12. Run validators; surface failures as test report, not prose — D5

---

## WHAT THIS PROMPT IS NOT

- Not a domain-specific prompt — applies to any multi-agent system
- Not a replacement for domain knowledge — these principles govern structure,
  not content
- Not a rigid template — principles take precedence over patterns derived
  from them; when a pattern conflicts with a principle, revise the pattern

---

## REUSE PATTERN

To scaffold a new agent system in any domain:

```
System prompt: [this file] + [domain-specific shared baseline]
User input:    "Design a multi-agent system for [domain]
                serving [consumer]
                under [compliance]
                for a [team type] team."
```

The AI will apply these principles and produce a system where:
- Constraints are enforced structurally, not instructionally
- Quality is tested, not self-certified
- New cases extend the system without modifying stable components
- The human confirms a manifest, not a label
- Every judgment call is a data lookup, not a runtime decision

---
