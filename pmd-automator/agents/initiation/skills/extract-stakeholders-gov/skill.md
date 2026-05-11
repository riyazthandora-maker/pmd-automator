# Skill: extract-stakeholders-gov
**Version:** 3.0
**Agent:** Initiation Agent
**Output:** `common/input/snippets/stakeholders_gov.md`

---

## Purpose

Extract named contacts and governance role assignments directly from the source files in `common/input/`. Produces Charter Section 7.

No ingestion step. No SOW anchor map. Files are read as-is from `common/input/`.

---

## Source Files & Target Sections

### Section 7a — Stakeholder Register
**File:** `common/input/purchase_order.md`
**Target heading:** `Contact Information` *(appears as `## 1. Contact Information`)*

The contact table in this file uses a two-column format (Vendor | Client). Parse both columns:

| Field | Vendor Column | Client Column |
|-------|--------------|---------------|
| Organisation | Innovate Tech Solutions LLC | TechVision Global Inc. |
| Contact Name | Sarah Chen | Robert Mitchell |
| Title | Program Manager | CEO & Founder |
| Email | sarah.chen@innovatetech.com | robert.mitchell@techvision.com |
| Phone | +1-415-555-0100 | +1-212-555-0200 |

Extract all labelled fields (`**Contact:**`, `**Email:**`, `**Phone:**`) from both columns. Build a normalized stakeholder table with columns: `Name | Role | Organisation | Involvement | Email`.

Assign RACI involvement:
- `CEO`, `Founder`, `Chief`, `Sponsor`, `Executive` → **Sponsor**
- `PM`, `Program Manager`, `Project Manager` → **Decision-maker**
- `Lead` (UX Lead, Backend Lead, etc.) → **Consulted**
- All others → **Informed**

---

### Section 7b — Governance Roles
**File:** `common/input/business_requirements.md`
**Target fields:** Document-level metadata labels at the top of the file (before the first `##` heading)

Look for these exact label patterns in the first 10 lines:
- `**Author:**` → maps to **Project Manager**
- `**Stakeholder Lead:**` → maps to **Project Sponsor**

Extract the name and title from the value following each label. Example:
- `**Author:** Sarah Chen (Program Manager)` → PM: Sarah Chen, Program Manager
- `**Stakeholder Lead:** Robert Mitchell (CEO)` → Sponsor: Robert Mitchell, CEO

Build a governance authority block:
```
**Project Manager:** <Name>, <Title> — Day-to-day delivery and schedule authority
**Project Sponsor:** <Name>, <Title> — Budget, strategic authority, final approver
**Steering Committee:** <Sponsor Name> + additional Decision-maker contacts
```

---

## Extraction Logic

### Contact table (purchase_order.md)
1. Open `common/input/purchase_order.md`.
2. Strip YAML front-matter.
3. Find the heading containing `Contact Information` (substring match, case-insensitive).
4. Extract all lines until the next `##` heading.
5. Parse the two-column Markdown table: split each row by `|`, trim cells, extract `**Contact:**`, `**Email:**`, `**Phone:**` values using regex `\*\*<label>\*\*\s*(.+)`.

### Governance metadata (business_requirements.md)
1. Open `common/input/business_requirements.md`.
2. Read the document header (lines before the first `##` heading).
3. For each of `Author`, `Stakeholder Lead`: apply regex `\*\*<label>:\*\*\s*(.+)` to extract the full value string.
4. Parse name and title from the value — name is the text before the first `(`, title is inside `()`.

**No anchor tags required.**

---

## Output Format

Write to `common/input/snippets/stakeholders_gov.md`:

```markdown
---
skill: extract-stakeholders-gov
version: "3.0"
extracted_at: <ISO-8601>
sources:
  - common/input/purchase_order.md        → Contact Information (Section 1)
  - common/input/business_requirements.md → Author, Stakeholder Lead (header labels)
---

## 7. Governance & Authority

### 7a. Stakeholder Register
| Name | Role | Organisation | Involvement | Email |
|------|------|--------------|-------------|-------|
<parsed contact rows — both vendor and client>

### 7b. Governance & Authority
**Project Manager:** <Name>, <Title> — Day-to-day delivery and schedule authority
**Project Sponsor:** <Name>, <Title> — Budget and strategic authority; final approver
**Steering Committee:** <Sponsor> + <additional Decision-maker names>
```

---

## Failure Modes

| Scenario | Action |
|---------|--------|
| Source file missing | Write `<!-- NOT_FOUND: <file> -->`; continue |
| Contact table not found | Write `<!-- NOT_FOUND: contact_information -->`; continue |
| Author/Stakeholder Lead labels absent | Write `<!-- NOT_FOUND: governance_fields --> ⚠ Requires manual entry`; continue |
| Name cannot be parsed from cell | Use `Unknown Party N` with `⚠` flag |
