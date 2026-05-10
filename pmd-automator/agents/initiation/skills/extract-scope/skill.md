# Skill: Extract Scope

**Agent:** Initiation Agent
**Skill ID:** `initiation.extract-scope`
**Depends on:** `initiation.ingestion` (source file must exist in `02_working_docs/`)
**Anchor map:** `common/templates/sow_map.md` → anchor `scope`

---

## Purpose

Locate and extract the project scope section from an ingested working document, then write a clean, structured Markdown snippet to `03_ai_snippets/` for downstream consumption by the charter-generation skill.

---

## Trigger

- Invoked after ingestion completes (`state.status == "INGESTED"`)
- Can be run manually against any `.md` file in `02_working_docs/`

---

## Inputs

| Source | Description |
|--------|-------------|
| `02_working_docs/<name>.md` | Ingested Markdown document to extract from |
| `common/templates/sow_map.md` | Anchor registry (anchor ID: `scope`) |

---

## Algorithm

```
1. LOAD    source file from 02_working_docs/<name>.md

2. ANCHOR SCAN
   a. Search for opening tag:  <!-- anchor:scope -->
   b. Search for closing tag:  <!-- anchor:scope:end -->
   c. If both found → extract content between them verbatim

3. FALLBACK (if no anchors found)
   a. Scan headings for patterns from sow_map.md:
      "scope", "project scope", "statement of work",
      "work scope", "in scope", "out of scope"
   b. Extract from matched heading until the next heading
      of equal or higher level (##, #)

4. CLEAN
   a. Strip anchor comment tags from extracted text
   b. Normalise heading levels (top-level heading → ##)
   c. Deduplicate blank lines (max 1 consecutive blank line)

5. WRAP in snippet envelope (see Output Format below)

6. WRITE to 03_ai_snippets/<name>_scope.md
```

---

## Output Format

```markdown
---
skill: extract-scope
source: <name>.md
extracted_at: <ISO-8601>
anchor: scope
---

## Scope

<!-- extracted content here -->

### In Scope

- ...

### Out of Scope

- ...
```

---

## Output Location

```
projects/project_alpha/03_ai_snippets/<source-stem>_scope.md
```

---

## Failure Modes

| Condition | Behaviour |
|-----------|-----------|
| Source file not found in `02_working_docs/` | Raise `FileNotFoundError`; log and abort |
| No anchor tags and no fallback heading match | Write empty snippet with `<!-- NO_SCOPE_FOUND -->` comment; log warning |
| Anchor open tag present but no close tag | Extract from open tag to next equal/higher heading |
| Multiple scope anchors in one document | Extract all matches; concatenate with `---` separator |

---

## State Effect

None — this skill is read-only relative to the state file. The charter-generation skill reads `03_ai_snippets/` directly.

---

## Downstream

`03_ai_snippets/<name>_scope.md` → consumed by `initiation.generate-charter` to populate **Section 4: Scope** of `charter_master.md`.
