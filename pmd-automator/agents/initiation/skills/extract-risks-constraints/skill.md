# Skill: extract-risks-constraints
**Version:** 3.0
**Agent:** Initiation Agent
**Output:** `common/input/snippets/risks_constraints.md`

---

## Purpose

Extract project constraints, non-functional requirements, and evaluation criteria directly from the source files in `common/input/`. Synthesizes Charter Section 6.

No ingestion step. No SOW anchor map. Files are read as-is from `common/input/`.

---

## Source Files & Target Sections

### Section 6a — Project Constraints
**File:** `common/input/business_requirements.md`
**Target heading:** `Project Constraints` *(appears as `## 6. Project Constraints`)*

Extract the full bullet list under this heading. Tag each constraint by type:
- Contains "timeline", "week", "month" → `[Timeline]`
- Contains "budget", "cost", "USD", "$" → `[Budget]`
- Contains "parity", "platform", "iOS", "Android" → `[Technical]`
- Otherwise → `[Other]`

---

### Section 6b — Non-Functional Requirements & Derived Risks
**File:** `common/input/business_requirements.md`
**Target heading:** `Non-Functional Requirements` *(appears as `## 5. Non-Functional Requirements`)*

Extract the full list. For each NFR item, produce a corresponding risk row:
- "JWT Authentication and 80%+ code coverage" → Risk: *Insufficient test coverage may allow security vulnerabilities to reach production.*
- "Data must be encrypted at rest and in transit" → Risk: *Non-compliance with encryption standards exposes the project to HIPAA/GDPR penalties.*
- "API response time under 200 ms" → Risk: *Performance degradation under load could cause poor UX and SLA breach.*

Format as a Markdown table with columns: `Risk Description | Source | Impact | Probability | Mitigation`.
Assign default ratings when not explicitly stated: Impact = `Medium`, Probability = `Medium`.

---

### Section 6c — Evaluation Criteria Cross-Reference
**File:** `common/input/rfp_summary.md`
**Target heading:** `Evaluation Criteria` *(appears as `## D. Evaluation Criteria`)*

Extract the full list. Each criterion that requires a technical capability is a latent risk. Tag with `[Evaluation Criteria]` as source. Example:
- "AI Model Robustness" → Risk: *AI health-risk prediction model may not meet client accuracy expectations.*
- "Timeline & Budget" → Risk: *Fixed 24-week / $450K envelope leaves no contingency margin.*

---

## Extraction Logic

1. Open the target file from `common/input/`.
2. Strip YAML front-matter.
3. Scan for a `##` heading whose text **contains** the target keyword (case-insensitive substring match — handles `## 5. Non-Functional Requirements`, `## 6. Project Constraints`, `## D. Evaluation Criteria` without exact matching).
4. Collect all lines until the next `##` heading of equal or higher level.
5. Return the heading + body block.

**No anchor tags required.**

---

## Output Format

Write to `common/input/snippets/risks_constraints.md`:

```markdown
---
skill: extract-risks-constraints
version: "3.0"
extracted_at: <ISO-8601>
sources:
  - common/input/business_requirements.md → project_constraints, non_functional_requirements
  - common/input/rfp_summary.md           → evaluation_criteria
---

## 6. Risks, Assumptions & Constraints

### 6a. Project Constraints
<tagged constraint list from business_requirements.md → Project Constraints>

### 6b. Non-Functional Requirements & Derived Risks
<risk table derived from business_requirements.md → Non-Functional Requirements>

### 6c. Evaluation Criteria Cross-Reference
<risk rows derived from rfp_summary.md → Evaluation Criteria>

### 6d. Assumptions
- TBC — to be completed by the Project Manager.
```

---

## Failure Modes

| Scenario | Action |
|---------|--------|
| Source file missing | Write `<!-- NOT_FOUND: <file> -->`; continue |
| Target heading not found | Write `<!-- NOT_FOUND: <section_name> -->`; continue |
| NFR list found but risk inference ambiguous | Log NFR verbatim; set Impact/Probability = `TBC ⚠` |
