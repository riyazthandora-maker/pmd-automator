# Skill: Extract Risks

**Agent:** Initiation Agent
**Skill ID:** `initiation.extract-risks`
**Depends on:** `initiation.ingestion` (source file must exist in `02_working_docs/`)
**Anchor map:** `common/templates/sow_map.md` → anchor `risks`

---

## Purpose

Locate and extract risk information from an ingested working document. Parse any prose, lists, or existing tables into a **normalised risk table** with mandatory `Impact` and `Probability` columns. Write the result to `03_ai_snippets/` for downstream charter generation.

---

## Trigger

- Invoked after ingestion completes (`state.status == "INGESTED"`)
- Can be run manually against any `.md` file in `02_working_docs/`

---

## Inputs

| Source | Description |
|--------|-------------|
| `02_working_docs/<name>.md` | Ingested Markdown document to extract from |
| `common/templates/sow_map.md` | Anchor registry (anchor ID: `risks`) |

---

## Algorithm

```
1. LOAD    source file from 02_working_docs/<name>.md

2. ANCHOR SCAN
   a. Search for opening tag:  <!-- anchor:risks -->
   b. Search for closing tag:  <!-- anchor:risks:end -->
   c. If both found → extract content between them verbatim

3. FALLBACK (if no anchors found)
   a. Scan headings for patterns from sow_map.md:
      "risk", "risks", "risk register", "risk assessment",
      "risk and issues", "identified risks"
   b. Extract from matched heading until the next heading
      of equal or higher level (##, #)

4. PARSE — detect input format and normalise to rows:
   a. Existing Markdown table  → parse columns; map to canonical fields
   b. Bulleted list            → each bullet = one risk row; infer fields from text
   c. Prose paragraph          → sentence-level split; each sentence = one risk row

5. NORMALISE each row to canonical fields:
   - Risk Description  (required)
   - Impact            (required) — allowed values: Critical / High / Medium / Low
   - Probability       (required) — allowed values: High / Medium / Low
   - Mitigation        (optional) — empty string if not found

   For fields that cannot be inferred, default to "TBC".

6. RENDER output table (see Output Format below)

7. WRITE to 03_ai_snippets/<name>_risks.md
```

---

## Output Format

```markdown
---
skill: extract-risks
source: <name>.md
extracted_at: <ISO-8601>
anchor: risks
---

## Risk Register

| # | Risk Description | Impact | Probability | Mitigation |
|---|-----------------|--------|-------------|------------|
| 1 | <description> | High | Medium | <mitigation or TBC> |
| 2 | <description> | Critical | Low | <mitigation or TBC> |
```

### Impact scale

| Level | Definition |
|-------|-----------|
| Critical | Project failure or major contractual breach |
| High | Significant cost, schedule, or scope impact |
| Medium | Moderate impact; manageable with effort |
| Low | Minor nuisance; easily absorbed |

### Probability scale

| Level | Definition |
|-------|-----------|
| High | > 60% likelihood |
| Medium | 30–60% likelihood |
| Low | < 30% likelihood |

---

## Output Location

```
projects/project_alpha/03_ai_snippets/<source-stem>_risks.md
```

---

## Failure Modes

| Condition | Behaviour |
|-----------|-----------|
| Source file not found in `02_working_docs/` | Raise `FileNotFoundError`; log and abort |
| No anchor and no fallback heading match | Write table shell with one placeholder row; log warning |
| Risk row missing both Impact and Probability | Default both to `TBC`; flag row with `⚠` prefix |
| Existing table has extra columns | Preserve as additional columns appended after Mitigation |

---

## State Effect

None — read-only relative to state file.

---

## Downstream

`03_ai_snippets/<name>_risks.md` → consumed by `initiation.generate-charter` to populate **Section 8: Risks** of `charter_master.md`.
