# Skill: Extract Stakeholders

**Agent:** Initiation Agent
**Skill ID:** `initiation.extract-stakeholders`
**Depends on:** `initiation.ingestion` (source file must exist in `02_working_docs/`)
**Anchor map:** `common/templates/sow_map.md` → anchor `stakeholders`

---

## Purpose

Locate and extract stakeholder and project team information from an ingested working document. Normalise any format (table, list, prose) into a consistent stakeholder register and write it to `03_ai_snippets/`.

---

## Trigger

- Invoked after ingestion completes (`state.status == "INGESTED"`)
- Can be run manually against any `.md` file in `02_working_docs/`

---

## Inputs

| Source | Description |
|--------|-------------|
| `02_working_docs/<name>.md` | Ingested Markdown document to extract from |
| `common/templates/sow_map.md` | Anchor registry (anchor ID: `stakeholders`) |

---

## Algorithm

```
1. LOAD    source file from 02_working_docs/<name>.md

2. ANCHOR SCAN
   a. Search for opening tag:  <!-- anchor:stakeholders -->
   b. Search for closing tag:  <!-- anchor:stakeholders:end -->
   c. If both found → extract content between them verbatim

3. FALLBACK (if no anchors found)
   a. Scan headings for patterns from sow_map.md:
      "stakeholder", "stakeholders", "team", "project team",
      "contacts", "key contacts", "participants"
   b. Extract from matched heading until the next heading
      of equal or higher level (##, #)

4. PARSE — detect input format and normalise to rows:
   a. Existing Markdown table → parse columns; map to canonical fields
   b. Bulleted list           → each bullet = one stakeholder row
   c. Prose paragraph         → extract Name + Role pairs using NLP-like
                                 heuristics (title-cased words near role keywords)

5. NORMALISE each row to canonical fields:
   - Name         (required)
   - Role / Title (required)
   - Organisation (optional)
   - Involvement  (optional) — e.g. Sponsor, Decision-maker, Informed, Consulted
   - Contact      (optional) — email or phone if present

   For fields that cannot be inferred, default to "TBC".

6. DEDUPLICATE rows by Name (case-insensitive); keep the row with more fields populated.

7. RENDER output table (see Output Format below)

8. WRITE to 03_ai_snippets/<name>_stakeholders.md
```

---

## Output Format

```markdown
---
skill: extract-stakeholders
source: <name>.md
extracted_at: <ISO-8601>
anchor: stakeholders
---

## Stakeholder Register

| Name | Role | Organisation | Involvement | Contact |
|------|------|--------------|-------------|---------|
| Jane Smith | Project Sponsor | ACME Corp | Decision-maker | jane@example.com |
| John Doe | Technical Lead | ACME Corp | Consulted | TBC |
```

### Involvement levels (RACI-aligned)

| Level | Meaning |
|-------|---------|
| Sponsor | Final authority; owns the budget |
| Decision-maker | Approves key outputs |
| Consulted | Subject-matter expert; provides input |
| Informed | Receives updates; no approval role |

---

## Output Location

```
projects/project_alpha/03_ai_snippets/<source-stem>_stakeholders.md
```

---

## Failure Modes

| Condition | Behaviour |
|-----------|-----------|
| Source file not found in `02_working_docs/` | Raise `FileNotFoundError`; log and abort |
| No anchor and no fallback heading match | Write table shell with one placeholder row; log warning |
| Name cannot be determined for a row | Use `Unknown Party N`; flag with `⚠` prefix |
| Duplicate names after deduplication | Merged row logged with note: `(merged from N occurrences)` |

---

## State Effect

None — read-only relative to state file.

---

## Downstream

`03_ai_snippets/<name>_stakeholders.md` → consumed by `initiation.generate-charter` to populate **Section 6: Stakeholders** of `charter_master.md`.
