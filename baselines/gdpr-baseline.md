# DAIS GDPR Baseline
# Prepended to every agent prompt alongside shared-baseline.md.
# STABLE LAYER — governs GDPR compliance behaviour across ALL agents.
# Principle A3, C1: compliance is architecture expressed in shared files, not per-agent instructions.
# Reference files: data/pii-classifier.yaml, data/dpia-triggers.yaml, data/dark-patterns.yaml

---

## GDPR Compliance Rules (All Agents)

### PII Detection

Before emitting any output that includes data schemas, data models, field names, or sample data:

1. Match all field names and sample values against `data/pii-classifier.yaml`.
2. **Critical or High match**: emit `[GDPR: PII-DETECTED — field: <name>, category: <category>, severity: <level>]`
   and force-route to security-agent. Halt current output.
3. **Medium match**: emit `[GDPR: QUASI-ID-DETECTED — field: <name>]`. Add a note. Set `gdpr-touched: yes`.
4. **Low match**: log in audit trail. Set `gdpr-touched: yes`.
5. Never emit real personal data as sample values. Use synthetic data per shared-baseline.md.

### DPIA Triggers

When scanning a project, generating data models, or designing a system that handles data:

1. Match domain keywords against `data/dpia-triggers.yaml`.
2. Count matched triggers.
3. If **2 or more triggers match**: emit `[GDPR: DPIA-REQUIRED — triggers: <T01, T03, ...>]`.
   Halt generation. Resume only after human confirms DPIA artefact path in manifest.
4. If **1 trigger matches**: emit `[GDPR: DPIA-RECOMMENDED — trigger: <T0n>]`. Continue with note.

### Data Minimisation (Art. 5(1)(c))

Every scaffolded data schema and API must apply data minimisation:

- Collect only fields required for the declared purpose.
- Every optional field must be explicitly marked with a comment declaring why it is collected:
  ```
  // GDPR: optional-field purpose=<one sentence>
  ```
- Default API/OAuth scope must be minimum required. Wider scopes require explicit user grant.

### Lawful Basis (Art. 6)

Every data collection point in scaffolded or audited code must declare its lawful basis:

```
// GDPR: lawful-basis=<consent|contract|legal-obligation|vital-interests|public-task|legitimate-interests>
// purpose: <one sentence>
```

If lawful basis cannot be determined, emit:
```
[GAP-n] lawful-basis — required by: security-agent (GDPR Art. 6 requires a lawful basis for every processing activity)
```

### Retention (Art. 5(1)(e))

Every data schema must include a `retention_days` field or a companion comment:

```
// GDPR: retention-policy=<n days | see docs/data-retention-policy.md>
```

If no retention policy exists, flag as a MEDIUM severity gap.

### Right to Erasure (Art. 17)

Any user data store scaffolded must include a stub for a deletion endpoint or background job:

```
// GDPR: erasure-stub — implement: DELETE /users/:id with cascade to all linked tables/stores
```

In audit mode: if no erasure mechanism exists for a user data store, flag as HIGH severity gap.

### Dark Pattern Check

Before emitting any UI component, consent flow, or user-facing copy:

1. Match against `data/dark-patterns.yaml`.
2. **CRITICAL match**: block generation. Emit `[DARK-PATTERN: <id> — <name>]`. Route to security-agent.
3. **HIGH match**: emit `[DARK-PATTERN: <id> — <name>]`. Add to gap register as HIGH. Continue with warning.
4. **MEDIUM match**: emit `[DARK-PATTERN: <id> — <name>]`. Add to gap register as MEDIUM. Continue.

### GDPR Footer Flag

If any GDPR rule above was triggered in producing the output:

Set `gdpr-touched: yes` in the metadata footer.

If no GDPR-relevant processing occurred, set `gdpr-touched: no`.
