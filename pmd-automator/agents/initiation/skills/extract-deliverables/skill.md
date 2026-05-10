# Skill: Extract Deliverables

**Agent:** Initiation Agent
**Skill ID:** `initiation.extract-deliverables`
**Depends on:** `initiation.ingestion` (source file must exist in `02_working_docs/`)
**Anchor map:** `common/templates/sow_map.md` → anchor `deliverables`

---

## Purpose

Locate and extract all project deliverables and milestones from an ingested working document. Normalise into a structured deliverable register and write a Markdown snippet to `03_ai_snippets/`.

---

## Trigger

- Invoked after ingestion completes (`state.status == "INGESTED"`)
- Can be run manually against any `.md` file in `02_working_docs/`

---

## Inputs

| Source | Description |
|--------|-------------|
| `02_working_docs/<name>.md` | Ingested Markdown document to extract from |
| `common/templates/sow_map.md` | Anchor registry (anchor ID: `deliverables`) |

---

## Algorithm

```
1. LOAD    source file from 02_working_docs/<name>.md

2. ANCHOR SCAN
   a. Search for opening tag:  <!-- anchor:deliverables -->
   b. Search for closing tag:  <!-- anchor:deliverables:end -->
   c. If both found → extract content between them verbatim

3. FALLBACK (if no anchors found)
   a. Scan headings for patterns from sow_map.md:
      "deliverable", "deliverables", "outputs", "milestones",
      "key outputs", "project outputs"
   b. Extract from matched heading until the next heading
      of equal or higher level (##, #)

4. PARSE — detect input format and normalise to rows:
   a. Existing Markdown table → parse columns; map to canonical fields
   b. Numbered/bulleted list  → each item = one deliverable row
   c. Prose paragraph         → sentence-level split; extract noun-phrase
                                 candidates using keyword heuristics
                                 (words near "deliver", "produce", "submit",
                                  "complete", "milestone", "report", "document")

5. NORMALISE each row to canonical fields:
   - #              (auto-incremented sequence number)
   - Deliverable    (required) — name or short description
   - Type           (optional) — Document / Report / Software / Presentation / Approval / Other
   - Owner          (optional) — responsible party if stated
   - Due Date       (optional) — parse date strings; normalise to YYYY-MM-DD
   - Acceptance Criteria (optional) — brief criterion if mentioned

   For fields that cannot be inferred, default to "TBC".

6. SORT rows by Due Date ascending (TBC rows placed at end)

7. RENDER output table (see Output Format below)

8. WRITE to 03_ai_snippets/<name>_deliverables.md
```

---

## Output Format

```markdown
---
skill: extract-deliverables
source: <name>.md
extracted_at: <ISO-8601>
anchor: deliverables
---

## Deliverable Register

| # | Deliverable | Type | Owner | Due Date | Acceptance Criteria |
|---|-------------|------|-------|----------|---------------------|
| 1 | Discovery Report | Document | TBC | 2026-06-01 | Signed off by Sponsor |
| 2 | Final Presentation | Presentation | TBC | 2026-07-15 | TBC |
| 3 | Deployed System | Software | TBC | TBC | TBC |
```

### Deliverable type definitions

| Type | Examples |
|------|---------|
| Document | Report, plan, charter, specification, policy |
| Software | Application, script, API, integration, database |
| Presentation | Slide deck, workshop, demo |
| Approval | Sign-off, acceptance, UAT completion |
| Other | Physical output, training, process |

---

## Output Location

```
projects/project_alpha/03_ai_snippets/<source-stem>_deliverables.md
```

---

## Failure Modes

| Condition | Behaviour |
|-----------|-----------|
| Source file not found in `02_working_docs/` | Raise `FileNotFoundError`; log and abort |
| No anchor and no fallback heading match | Write table shell with one placeholder row; log warning |
| Date string unrecognisable | Store raw string in Due Date field; append `(unparsed)` |
| Duplicate deliverable names | Retain both; append `(duplicate?)` flag for human review |

---

## State Effect

None — read-only relative to state file.

---

## Downstream

`03_ai_snippets/<name>_deliverables.md` → consumed by `initiation.generate-charter` to populate **Section 5: Deliverables** of `charter_master.md`.
