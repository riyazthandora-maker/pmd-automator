# Skill: extract-milestones-finance
**Version:** 3.0
**Agent:** Initiation Agent
**Output:** `common/input/snippets/milestones_finance.md`

---

## Purpose

Extract deliverables, project plan phases, and payment terms directly from `common/input/purchase_order.md`. Produces Charter Section 5.

No ingestion step. No SOW anchor map. File is read as-is from `common/input/`.

---

## Source File

**File:** `common/input/purchase_order.md` (single source for all three sub-sections)

---

## Target Sections

### Section 5a — Deliverable Register
**Target heading:** `Services & Key Deliverables` *(appears as `## 3. Services & Key Deliverables`)*

The section contains a two-column Markdown table (`Deliverable | Timeline`). Extract all rows verbatim. Normalize timeline values to `Week N` format where possible.

Add a `Type` column by classifying each deliverable:
- Contains "document", "BRD", "report", "stories" → `Document`
- Contains "design", "mockup", "prototype", "UI", "UX" → `Design`
- Contains "app", "application", "source code", "build", "API", "backend", "database" → `Software`
- Contains "test", "audit", "security" → `Quality`
- Contains "deployment", "release", "store" → `Release`
- Otherwise → `Other`

---

### Section 5b — Project Plan Phases
**Target heading:** `High-Level Project Plan` *(appears as `## 4. High-Level Project Plan`)*

The section contains a four-column Markdown table (`Phase | Duration | Key Activities | Primary Owner`). Extract all rows verbatim. Do not reorder phases.

---

### Section 5c — Payment Schedule
**Target heading:** `Payment Terms` *(appears as `## 7. Payment Terms`)*

The section contains a two-column Markdown table (`Milestone | Payment %`). Extract all rows exactly as written — **do not round or alter percentages**. After extraction, sum all percentages and verify they total 100%. If not, append `⚠ SUM_MISMATCH: total is <N>%`.

---

## Extraction Logic

1. Open `common/input/purchase_order.md`.
2. Strip YAML front-matter.
3. For each target heading, scan for a `##` line whose text **contains** the keyword (case-insensitive substring match — handles `## 3. Services & Key Deliverables`, `## 4. High-Level Project Plan`, `## 7. Payment Terms` without requiring exact matches).
4. Collect all lines until the next `##` heading of equal or higher level.
5. Return the heading + body block.

**No anchor tags required.** If a heading is not found, write `<!-- NOT_FOUND: <section_name> -->` and continue.

---

## Output Format

Write to `common/input/snippets/milestones_finance.md`:

```markdown
---
skill: extract-milestones-finance
version: "3.0"
extracted_at: <ISO-8601>
sources:
  - common/input/purchase_order.md → Services & Key Deliverables, High-Level Project Plan, Payment Terms
payment_sum_check: <PASS|FAIL ⚠>
---

## 5. Summary Milestone Schedule & Payment Terms

### 5a. Deliverable Register
<table from purchase_order.md → Services & Key Deliverables, with added Type column>

### 5b. Project Plan Phases
<table from purchase_order.md → High-Level Project Plan>

### 5c. Payment Schedule
<table from purchase_order.md → Payment Terms>
```

---

## Failure Modes

| Scenario | Action |
|---------|--------|
| `purchase_order.md` missing | Write `<!-- NOT_FOUND: purchase_order.md -->`; halt skill |
| Target heading not found | Write `<!-- NOT_FOUND: <section_name> -->`; continue |
| Payment percentages do not sum to 100% | Append `⚠ SUM_MISMATCH`; include raw values as extracted |
| Timeline value cannot be normalized | Store raw text with `(unparsed)` suffix |
