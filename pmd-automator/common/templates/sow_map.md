# Document Anchor Map — Extraction Registry

Defines canonical anchor IDs and their expected heading patterns for the three standard input documents used by the Initiation Engine. Extraction skills use this map to locate sections regardless of minor heading wording variations.

> **Standard Inputs:** Skills operate exclusively on `rfp_summary.md`, `business_requirements.md`, and `purchase_order.md`. SOW references are not supported.

---

## Anchor Format

Anchors are HTML comments embedded in `02_working_docs/` Markdown files:

```markdown
<!-- anchor:background -->
## Background & Context

...section content...

<!-- anchor:background:end -->
```

If explicit anchors are absent, skills fall back to **heading pattern matching** using the `fallback_headings` lists below.

---

## Anchor Registry

### rfp_summary.md

| Anchor ID | Consumed By | Fallback Heading Patterns (case-insensitive) | → Charter |
|-----------|-------------|----------------------------------------------|-----------|
| `background` | `extract-scope-obj` | `background`, `background & context`, `background and context`, `context`, `project context`, `project background` | Section 2 |
| `evaluation_criteria` | `extract-risks-constraints` | `evaluation criteria`, `evaluation`, `scoring criteria`, `vendor criteria`, `assessment criteria`, `selection criteria` | Section 6 |

### business_requirements.md

| Anchor ID | Consumed By | Fallback Heading Patterns (case-insensitive) | → Charter |
|-----------|-------------|----------------------------------------------|-----------|
| `business_objective` | `extract-scope-obj` | `business objective`, `business objectives`, `business case`, `strategic objective`, `purpose`, `project purpose`, `goals` | Section 3 |
| `functional_requirements` | `extract-scope-obj` | `functional requirements`, `functional requirement`, `feature requirements`, `features`, `system requirements`, `fr-1` | Section 4 |
| `non_functional_requirements` | `extract-risks-constraints` | `non-functional requirements`, `non functional requirements`, `nfr`, `quality requirements`, `performance requirements`, `security requirements` | Section 6 |
| `project_constraints` | `extract-risks-constraints` | `project constraints`, `constraints`, `timeline constraints`, `budget constraints`, `limitations`, `scope limitations` | Section 6 |
| `governance_fields` | `extract-stakeholders-gov` | `author`, `prepared by`, `stakeholder lead`, `document owner`, `approver`, `governance`, `document control` | Section 7 |

### purchase_order.md

| Anchor ID | Consumed By | Fallback Heading Patterns (case-insensitive) | → Charter |
|-----------|-------------|----------------------------------------------|-----------|
| `contact_information` | `extract-stakeholders-gov` | `contact information`, `contacts`, `key contacts`, `parties`, `party information`, `vendor contact`, `client contact` | Section 7 |
| `key_deliverables` | `extract-milestones-finance` | `key deliverables`, `deliverables`, `deliverable schedule`, `project deliverables`, `outputs`, `scope of work` | Section 5 |
| `project_plan` | `extract-milestones-finance` | `high-level project plan`, `project plan`, `work plan`, `project phases`, `phases`, `timeline`, `schedule` | Section 5 |
| `payment_terms` | `extract-milestones-finance` | `payment terms`, `payment schedule`, `invoice schedule`, `billing milestones`, `financial terms`, `payments` | Section 5 |

---

## Anchor Placement Rules

1. Open tag `<!-- anchor:<id> -->` placed on the line immediately before the section heading.
2. Close tag `<!-- anchor:<id>:end -->` placed on the line immediately after the last paragraph of the section.
3. Nested sub-sections between open and close tags are included in the extraction.
4. If both open and close tags are present, content between them is extracted verbatim.
5. If only an open tag is present, content is extracted until the next same-level or higher heading.

---

## Example Annotated Input Files

### rfp_summary.md
```markdown
<!-- anchor:background -->
## A. Background & Context

TechVision's digital transformation rate stands at 10%, below the industry peer standard...

<!-- anchor:background:end -->

<!-- anchor:evaluation_criteria -->
## D. Evaluation Criteria

- Technical Expertise: Swift and Kotlin native development proficiency
- AI Model Robustness: quality of health-risk prediction model
<!-- anchor:evaluation_criteria:end -->
```

### business_requirements.md
```markdown
<!-- anchor:business_objective -->
## Business Objective

Increase digital transformation rate and market share...

<!-- anchor:business_objective:end -->

<!-- anchor:functional_requirements -->
## Functional Requirements

- FR-1: Wearable Sync (Apple HealthKit / Google Fit)
- FR-2: AI Health Risk Engine
<!-- anchor:functional_requirements:end -->

<!-- anchor:project_constraints -->
## Project Constraints

- 6-month timeline
- USD 450K budget cap
<!-- anchor:project_constraints:end -->
```

### purchase_order.md
```markdown
<!-- anchor:contact_information -->
## Contact Information

| Party | Name | Role | Email |
|-------|------|------|-------|
| Vendor PM | Sarah Chen | Project Manager | sarah.chen@innovatetech.com |
<!-- anchor:contact_information:end -->

<!-- anchor:payment_terms -->
## Payment Terms

- Kickoff: 30%
- Design Sign-off (Wk6): 25%
<!-- anchor:payment_terms:end -->
```

---

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-05-09 | Initial anchor registry (SOW-based) |
| 2.0 | 2026-05-10 | Migrated to 3-file input system; added per-file anchor registry for rfp_summary, business_requirements, purchase_order |
