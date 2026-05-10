# Initiation Agent — Orchestrator Runbook
**Version:** 2.0
**Agent:** Initiation Agent
**Location:** `agents/initiation/`
**Executor:** `runner.py`

---

## Purpose

Operate as a centralized, single-input processor. Reads three fixed source documents from `/common/input/`, runs four extraction skills in parallel, and assembles a professional HTML Project Charter at `/shared_output/Project_Charter.html`.

> No project registry lookup. No project-specific subdirectories. No state files.
> Drop files into `/common/input/` and press **Process**.

---

## 1. Input Resolution

The engine does **not** search for project-specific subdirectories. All source files are read from a single, fixed location:

```
INPUT_DIR = common/input/
```

Required files — these three must exist before the engine starts:

| File | Content |
|------|---------|
| `common/input/rfp_summary.md` | RFP background, scope of services, evaluation criteria |
| `common/input/business_requirements.md` | Business objectives, functional requirements, constraints, NFRs |
| `common/input/purchase_order.md` | Deliverables schedule, project plan, payment terms, contacts |

**Pre-flight check** (performed by `runner.py` before any stage runs):
- Confirm all three files exist at the paths above.
- If any file is missing, emit `stage_error` with a message naming the missing file and halt immediately.
- No schema validation, no anchor completeness check — proceed directly to extraction.

> The following paths are **removed** from this engine's scope and must not be referenced:
> - ~~`projects/<PROJECT_ID>/`~~
> - ~~`02_working_docs/`~~
> - ~~`state/<PROJECT_ID>_state.json`~~
> - ~~`projects_registry.json`~~

---

<!--
## SUSPENDED — Stage 1: Ingestion (PDF → Markdown)

**Reason:** Engine now assumes Markdown files are pre-placed in /common/input/.
             PDF conversion is a pre-processing step handled outside this engine.

Invoke skill `initiation.ingestion`:
- Scan `[PROJECT_DIR]/00_inbox/` for PDFs.
- Convert, archive, and write to `[PROJECT_DIR]/02_working_docs/`.
- Validate that all three required files exist in `02_working_docs/`.

On success: emit `stage_done`; advance `STATE_FILE.status` to `"INGESTED"`.
On failure: emit `stage_error`; halt pipeline.
-->

<!--
## SUSPENDED — Stage 2: Validation (Schema / Anchor Completeness)

**Reason:** Engine proceeds directly to extraction. Missing sections produce
             NOT_FOUND amber warning boxes in the charter rather than blocking the run.

Run `agents/initiation/skills/validation/validator.py` against `[PROJECT_DIR]/02_working_docs/`:
- Load anchor schema from `common/validation/sow_headers.json`.
- For each required file, verify presence of all declared anchor IDs.
- Emit `validation_error` events with human-readable messages.
- Halt if any required file is entirely absent.

On success: emit `stage_done`; advance `STATE_FILE.status` to `"VALIDATED"`.
-->

---

## 2. Stage 1 — Extraction
**Mode: Parallel** (all four skills run concurrently via `ThreadPoolExecutor`)

All skills read directly from `common/input/`. Snippets are written to `common/input/snippets/`.

| Skill | Reads from `common/input/` | Anchors Consumed | Output Snippet | Charter Sections |
|-------|---------------------------|-----------------|----------------|-----------------|
| `extract-scope-obj` | `rfp_summary.md`, `business_requirements.md` | `background`, `business_objective`, `functional_requirements` | `snippets/scope_obj.md` | 2, 3, 4 |
| `extract-risks-constraints` | `business_requirements.md`, `rfp_summary.md` | `project_constraints`, `non_functional_requirements`, `evaluation_criteria` | `snippets/risks_constraints.md` | 6 |
| `extract-stakeholders-gov` | `purchase_order.md`, `business_requirements.md` | `contact_information`, `governance_fields` | `snippets/stakeholders_gov.md` | 7 |
| `extract-milestones-finance` | `purchase_order.md` | `key_deliverables`, `project_plan`, `payment_terms` | `snippets/milestones_finance.md` | 5 |

**Anchor extraction order** (applied per skill, per section):
1. Look for explicit tag: `<!-- anchor:<id> -->` … `<!-- anchor:<id>:end -->`
2. Fall back to case-insensitive heading pattern matching (patterns defined in `common/validation/sow_headers.json`)
3. If neither found: write `<!-- NOT_FOUND: <anchor_id> -->` placeholder — **do not halt**

Wait for all four skills to complete before advancing to Stage 2.

If a skill fails entirely: emit `stage_warning`; continue with remaining skills.
If all four skills fail: emit `stage_error` and halt.

On completion: emit `stage_done` for `extraction`.

---

## 3. Stage 2 — HTML Assembly
**Mode: Sequential**

Assemble a professional HTML Project Charter from the four snippet files.

### 3.1 Load Snippets

Read from `common/input/snippets/`:
- `scope_obj.md`
- `milestones_finance.md`
- `risks_constraints.md`
- `stakeholders_gov.md`

Strip YAML front-matter from each before insertion.
If a snippet file is missing, substitute `<!-- NOT_FOUND: <name> -->`.

### 3.2 Section Order

Assemble in the order defined by `common/templates/charter_master.md`:

| # | Charter Section | Source |
|---|----------------|--------|
| 1 | Project Overview | Generated at runtime (timestamp, prepared-by) |
| 2 | Project Purpose & Business Case | `scope_obj.md` → Section 2 |
| 3 | Project Objectives & Success Criteria | `scope_obj.md` → Section 3 |
| 4 | High-Level Requirements | `scope_obj.md` → Section 4 |
| 5 | Summary Milestone Schedule & Payment Terms | `milestones_finance.md` → Section 5 |
| 6 | Risks, Assumptions & Constraints | `risks_constraints.md` → Section 6 |
| 7 | Governance & Authority | `stakeholders_gov.md` → Section 7 |
| 8 | Approval & Sign-off | Static block — do not extract; leave as pending |

### 3.3 Write Output

Convert snippets from Markdown → HTML using an inline converter (handles headings, tables, bullet lists, bold/italic, and `NOT_FOUND` placeholders rendered as amber warning boxes).

Write the final file to:
```
shared_output/Project_Charter.html
```

Emit `complete` event with `html_path` key. `app.py` reads this and auto-opens the file in the user's default browser.

---

## 4. Event Schema

All events are emitted as newline-delimited JSON to stdout (consumed by `app.py`):

```json
{ "event": "stage_start",    "stage": "<name>", "step": <n>, "total": 2, "ts": "<ISO-8601>" }
{ "event": "stage_progress", "stage": "<name>", "sub_pct": 0.0–1.0, "label": "<msg>", "ts": "<ISO-8601>" }
{ "event": "stage_done",     "stage": "<name>", "step": <n>, "total": 2, "ts": "<ISO-8601>" }
{ "event": "stage_error",    "stage": "<name>", "error": "<msg>", "ts": "<ISO-8601>" }
{ "event": "stage_warning",  "detail": "<msg>", "ts": "<ISO-8601>" }
{ "event": "complete",       "html_path": "<abs-path>", "ts": "<ISO-8601>" }
```

> `"total"` is always `2` (extraction + assembly). Ingestion and Validation events are no longer emitted.

---

## 5. State Lifecycle

| Stage | Status |
|-------|--------|
| Pre-flight file check | `PENDING` → error if files missing |
| Stage 1 (Extraction) complete | `EXTRACTED` |
| Stage 2 (Assembly) complete | `ASSEMBLED` — output at `shared_output/Project_Charter.html` |

> State files (`state/<id>_state.json`) are no longer written. Status is tracked in-memory within the runner process only.

---

## 6. Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Extraction + Assembly passed; HTML charter generated |
| `1` | Pre-flight file check failed, or all extraction skills failed, or assembly failed |

---

## 7. CLI Invocation

```bash
# Run the engine — no arguments required
python agents/initiation/runner.py
```

The engine resolves all paths relative to the repository root. No `--project-id`, `--project-root`, or `--state` arguments are needed or accepted.
