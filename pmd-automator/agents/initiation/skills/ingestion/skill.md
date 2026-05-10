# Skill: PDF Ingestion

**Agent:** Initiation Agent
**Skill ID:** `initiation.ingestion`
**Executor:** `parser.py`

---

## Purpose

Monitor `projects/<project_id>/00_inbox/` for newly dropped PDF files, convert each to Markdown, persist the outputs to the appropriate pipeline stages, and advance the project state machine.

---

## Trigger

- **Watch mode:** file-system event on `00_inbox/` (`.pdf` extension, `on_created`)
- **One-shot mode:** manual invocation to drain all pending PDFs in `00_inbox/`

---

## Inputs

| Source | Description |
|--------|-------------|
| `00_inbox/*.pdf` | Raw PDF documents submitted by the project team |
| `state/project_alpha_state.json` | Current project state (read for idempotency check) |

---

## Algorithm

```
FOR each .pdf file in 00_inbox/:

  1. HASH   — compute SHA-256 of the PDF
  2. CHECK  — if hash already present in state.documents → SKIP (idempotent)
  3. CONVERT — call pdf_to_markdown() with backend priority:
                 pymupdf4llm → marker-pdf → pymupdf (fitz)
  4. ARCHIVE — copy original PDF → 01_raw_archive/<filename>.pdf  (immutable)
  5. WRITE  — write Markdown (with YAML front-matter) → 02_working_docs/<stem>.md
  6. STATE  — append document entry to state.documents[]
               set state.status = "INGESTED"
               write state/project_alpha_state.json
```

---

## Outputs

| Destination | Content |
|-------------|---------|
| `01_raw_archive/<name>.pdf` | Immutable copy of the original PDF |
| `02_working_docs/<name>.md` | Markdown conversion with YAML front-matter |
| `state/project_alpha_state.json` | Updated with new document entry and `status: INGESTED` |

### Working document front-matter

```yaml
---
source: brief.pdf
ingested_at: 2026-05-09T10:00:00+00:00
source_hash: sha256:<hex>
---
```

---

## State Schema

```json
{
  "project_id": "project_alpha",
  "status": "INGESTED",
  "last_updated": "<ISO-8601>",
  "documents": [
    {
      "source_filename": "brief.pdf",
      "source_hash": "<sha256-hex>",
      "ingested_at": "<ISO-8601>",
      "raw_archive_path": "01_raw_archive/brief.pdf",
      "working_doc_path": "02_working_docs/brief.md",
      "status": "INGESTED"
    }
  ]
}
```

### Status lifecycle

```
PENDING → INGESTED → (downstream agents advance further)
```

---

## PDF Conversion Backends (priority order)

| Priority | Library | Notes |
|----------|---------|-------|
| 1 | `pymupdf4llm` | Lightweight, LLM-optimised markdown; preferred |
| 2 | `marker-pdf` | High-fidelity ML-based conversion; heavier |
| 3 | `pymupdf` (fitz) | Fallback plain-text extraction, page-by-page |

The skill tries each in order and uses the first that is installed. At least one must be present.

---

## Dependencies

See `requirements.txt` in this directory. Install with:

```bash
pip install -r agents/initiation/skills/ingestion/requirements.txt
```

Optional (enables real-time watch mode instead of polling):

```bash
pip install watchdog
```

---

## CLI Usage

```bash
# One-shot: drain all PDFs currently in 00_inbox
python agents/initiation/skills/ingestion/parser.py

# Watch mode: stay running, process new PDFs as they arrive
python agents/initiation/skills/ingestion/parser.py --watch

# Custom project root or state path
python agents/initiation/skills/ingestion/parser.py \
  --project-root projects/project_alpha \
  --state state/project_alpha_state.json \
  --watch \
  --poll-interval 15
```

---

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| No PDF backend installed | Raises `RuntimeError` with per-backend error list |
| Duplicate file (same hash) | Skipped with log message; state unchanged |
| Corrupt / unreadable PDF | Exception logged per file; remaining files continue |
| Missing inbox directory | `FileNotFoundError` raised immediately |
| State file missing | Initialised fresh with `status: PENDING` |

---

## Idempotency

The SHA-256 hash of each source PDF is stored in state. Re-dropping the same file (even under a different name) will be detected and skipped, preventing duplicate working documents.

---

## Downstream

After ingestion, the **Analysis Agent** (not yet implemented) should pick up files from `02_working_docs/` and advance state to `ANALYSED`.
