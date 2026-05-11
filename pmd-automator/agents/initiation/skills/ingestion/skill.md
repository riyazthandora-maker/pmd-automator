# Skill: ingestion
**Version:** 2.0
**Agent:** Initiation Agent
**Skill ID:** `initiation.ingestion`
**Executor:** `parser.py`

---

## Purpose

Monitor `[PROJECT_DIR]/00_inbox/` for newly dropped PDF files, convert each to Markdown, archive originals immutably, and validate that all three required input files are present before extraction begins.

---

## Dynamic Pathing

**Never hardcode a project name or path.** Resolve `PROJECT_DIR` at runtime:

1. Read `projects_registry.json` from the repository root.
2. Identify the active project (first entry with `"status": "Initiation"`, or the `--project-id` argument).
3. Derive:
   ```
   PROJECT_ID  = registry entry "id" field
   PROJECT_DIR = projects/<PROJECT_ID>/
   STATE_FILE  = state/<PROJECT_ID>_state.json
   ```

All paths below use `PROJECT_DIR` as the root.

---

## Trigger

- **Watch mode:** file-system event on `[PROJECT_DIR]/00_inbox/` (`.pdf` extension, `on_created`)
- **One-shot mode:** manual invocation to drain all pending PDFs in `00_inbox/`

---

## Required Input Files

After ingestion, the following three files **must** exist in `[PROJECT_DIR]/02_working_docs/`:

| Filename | Content |
|----------|---------|
| `rfp_summary.md` | RFP context, background, evaluation criteria |
| `business_requirements.md` | Business objectives, functional and non-functional requirements, constraints |
| `purchase_order.md` | Deliverables schedule, project plan, payment terms, contacts |

> **Strictly ignore** any file named `sow.md`, `statement_of_work.md`, or similar SOW variants. Do not process or archive them.

---

## Algorithm

```
1. RESOLVE — determine PROJECT_ID, PROJECT_DIR, STATE_FILE from registry

FOR each .pdf in [PROJECT_DIR]/00_inbox/:

  2. HASH    — compute SHA-256 of the PDF
  3. CHECK   — if hash already in STATE_FILE.documents → SKIP (idempotent)
  4. CONVERT — call pdf_to_markdown() with backend priority:
                 pymupdf4llm → marker-pdf → pymupdf (fitz)
  5. ARCHIVE — copy original PDF → [PROJECT_DIR]/01_raw_archive/<filename>.pdf  (immutable, never overwrite)
  6. WRITE   — write Markdown with YAML front-matter → [PROJECT_DIR]/02_working_docs/<stem>.md
  7. STATE   — append document entry to STATE_FILE.documents[]
               set STATE_FILE.status = "INGESTED"
               write STATE_FILE

AFTER all PDFs processed:

  8. VALIDATE — confirm 02_working_docs/ contains all three required files (by filename)
               for each required file, check structural completeness via sow_headers.json
               missing file entirely   → raise FileNotFoundError, halt extraction
               file present but anchor-incomplete → log warning, continue
```

---

## Outputs

| Destination | Content |
|-------------|---------|
| `[PROJECT_DIR]/01_raw_archive/<name>.pdf` | Immutable copy of the original PDF — never modify |
| `[PROJECT_DIR]/02_working_docs/<name>.md` | Markdown conversion with YAML front-matter |
| `state/<PROJECT_ID>_state.json` | Updated with document entries and `status: INGESTED` |

### Working document front-matter

```yaml
---
skill: ingestion
source_filename: brief.pdf
source_hash: sha256:<hex>
ingested_at: <ISO-8601>
---
```

---

## State Schema

```json
{
  "project_id": "<PROJECT_ID>",
  "status": "INGESTED",
  "last_updated": "<ISO-8601>",
  "documents": [
    {
      "source_filename": "rfp_summary.pdf",
      "source_hash": "<sha256-hex>",
      "ingested_at": "<ISO-8601>",
      "raw_archive_path": "01_raw_archive/rfp_summary.pdf",
      "working_doc_path": "02_working_docs/rfp_summary.md",
      "status": "INGESTED"
    }
  ]
}
```

### Status lifecycle

```
PENDING → INGESTED → EXTRACTED → ASSEMBLED → VERIFIED
```

---

## PDF Conversion Backends (priority order)

| Priority | Library | Notes |
|----------|---------|-------|
| 1 | `pymupdf4llm` | Lightweight, LLM-optimised markdown; preferred |
| 2 | `marker-pdf` | High-fidelity ML-based conversion; heavier dependency |
| 3 | `pymupdf` (fitz) | Fallback plain-text extraction, page-by-page |

The skill tries each in order and uses the first that is installed. At least one must be present or a `RuntimeError` is raised.

---

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| All PDF backends fail | Raise `RuntimeError`; log per-backend error; halt |
| Required file missing after ingestion | Raise `FileNotFoundError`; halt extraction pipeline |
| Required file present but anchor-incomplete | Log `validation_warning` per missing anchor; continue |
| Duplicate file (same SHA-256 hash) | Skip silently; state unchanged |
| Corrupt / unreadable PDF | Log exception per file; continue with remaining files |
| `00_inbox/` directory missing | Raise `FileNotFoundError` immediately |
| `STATE_FILE` missing | Initialise fresh with `status: PENDING` |

---

## Idempotency

The SHA-256 hash of each source PDF is stored in state. Re-dropping the same file (even under a different name) is detected and skipped, preventing duplicate working documents.

---

## CLI Usage

```bash
# One-shot: drain all PDFs currently in 00_inbox
python agents/initiation/skills/ingestion/parser.py \
  --project-id <project_id>

# Watch mode: stay running, process new PDFs as they arrive
python agents/initiation/skills/ingestion/parser.py \
  --project-id <project_id> --watch

# Explicit paths (overrides registry lookup)
python agents/initiation/skills/ingestion/parser.py \
  --project-root projects/<project_id> \
  --state state/<project_id>_state.json \
  --poll-interval 15
```

---

## Dependencies

```bash
pip install -r agents/initiation/skills/ingestion/requirements.txt

# Optional: enables real-time watch mode instead of polling
pip install watchdog
```
