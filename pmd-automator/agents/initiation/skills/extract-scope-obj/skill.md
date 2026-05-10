# Skill: extract-scope-obj
**Version:** 3.0
**Agent:** Initiation Agent
**Output:** `common/input/snippets/scope_obj.md`

---

## Purpose

Extract project background, business objectives, and functional requirements directly from the source files in `common/input/`. Produces Charter Sections 2, 3, and 4.

No ingestion step. No SOW anchor map. Files are read as-is from `common/input/`.

---

## Source Files & Target Sections

### Section 2 — Project Purpose & Business Case
**File:** `common/input/rfp_summary.md`
**Target heading:** `Background & Context` *(appears as `## A. Background & Context`)*

Extract the full text under this heading. Retain all sentences and bullet points verbatim. This becomes the business case narrative in the charter.

---

### Section 3 — Project Objectives & Success Criteria
**File:** `common/input/business_requirements.md`
**Target heading:** `Business Objective` *(appears as `## 1. Business Objective`)*

Extract the full paragraph(s) under this heading. If the section contains quantitative targets (uptime %, budget cap, timeline weeks), retain them — they become the success criteria.

---

### Section 4 — High-Level Requirements
**File:** `common/input/business_requirements.md`
**Target heading:** `Functional Requirements` *(appears as `## 3. Functional Requirements`)*

Extract the complete table or list of functional requirements exactly as written. Preserve FR IDs (FR-1, FR-2, etc.), feature names, and descriptions. Do not summarize or merge rows.

---

## Extraction Logic

1. Open the target file from `common/input/`.
2. Strip any YAML front-matter (content between opening and closing `---`).
3. Scan each line for a `##` heading whose text **contains** the target keyword (case-insensitive, substring match — not exact match). This handles numbered/lettered prefixes such as `## A.`, `## 1.`, `## 3.` without failing.
4. Once the heading line is found, collect all lines below it until the next `##` heading of equal or higher level.
5. Return the heading line plus its body as the extracted block.

**No anchor tags required.** If a heading is not found, write `<!-- NOT_FOUND: <section_name> -->` and continue without halting.

---

## Output Format

Write to `common/input/snippets/scope_obj.md`:

```markdown
---
skill: extract-scope-obj
version: "3.0"
extracted_at: <ISO-8601>
sources:
  - common/input/rfp_summary.md        → background
  - common/input/business_requirements.md → business_objective, functional_requirements
---

## 2. Project Purpose & Business Case
<extracted content from rfp_summary.md → Background & Context>

## 3. Project Objectives & Success Criteria
<extracted content from business_requirements.md → Business Objective>

## 4. High-Level Requirements
<extracted content from business_requirements.md → Functional Requirements>
```

---

## Failure Modes

| Scenario | Action |
|---------|--------|
| `common/input/<file>` does not exist | Write `<!-- NOT_FOUND: <file> -->`; continue |
| Target heading not found in file | Write `<!-- NOT_FOUND: <section_name> -->`; continue |
| Section body is empty | Write placeholder with `⚠ EMPTY_SECTION`; continue |
