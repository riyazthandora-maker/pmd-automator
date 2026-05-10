# SOW Anchor Map

Defines the canonical anchor IDs and their expected heading patterns for a Statement of Work (SOW) or project brief document. Extraction skills use this map to locate sections regardless of minor heading wording variations.

---

## Anchor Format

Anchors are HTML comments embedded in `02_working_docs/` Markdown files:

```markdown
<!-- anchor:scope -->
## Project Scope

...section content...

<!-- anchor:scope:end -->
```

If explicit anchors are absent, skills fall back to **heading pattern matching** using the `fallback_headings` list below.

---

## Anchor Registry

| Anchor ID | Consumed By | Fallback Heading Patterns (case-insensitive) |
|-----------|-------------|----------------------------------------------|
| `scope` | `extract-scope` | `scope`, `project scope`, `statement of work`, `work scope`, `in scope`, `out of scope` |
| `risks` | `extract-risks` | `risk`, `risks`, `risk register`, `risk assessment`, `risk and issues`, `identified risks` |
| `stakeholders` | `extract-stakeholders` | `stakeholder`, `stakeholders`, `team`, `project team`, `contacts`, `key contacts`, `participants` |
| `deliverables` | `extract-deliverables` | `deliverable`, `deliverables`, `outputs`, `milestones`, `key outputs`, `project outputs` |

---

## Anchor Placement Rules

1. Open tag `<!-- anchor:<id> -->` placed on the line immediately before the section heading.
2. Close tag `<!-- anchor:<id>:end -->` placed on the line immediately after the last paragraph of the section.
3. Nested sub-sections between open and close tags are included in the extraction.
4. If both open and close tags are present, content between them is extracted verbatim.
5. If only an open tag is present, content is extracted until the next same-level or higher heading.

---

## Example Annotated SOW

```markdown
<!-- anchor:scope -->
## Project Scope

This engagement covers the design and deployment of ...

### In Scope
- Item A
- Item B

### Out of Scope
- Item C
<!-- anchor:scope:end -->

<!-- anchor:stakeholders -->
## Key Contacts

| Name | Role | Email |
|------|------|-------|
| Jane Smith | Sponsor | jane@example.com |
<!-- anchor:stakeholders:end -->

<!-- anchor:deliverables -->
## Deliverables

| Deliverable | Due Date |
|-------------|----------|
| Discovery Report | 2026-06-01 |
<!-- anchor:deliverables:end -->

<!-- anchor:risks -->
## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Key resource unavailable | High | Medium | Cross-train backup |
<!-- anchor:risks:end -->
```

---

## Versioning

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-05-09 | Initial anchor registry |
