# PMO Automator

A hierarchical multi-agent system for automating Project Management Office (PMO) workflows. Given three structured input documents (RFP, Business Requirements, Purchase Order), it extracts key sections in parallel and assembles a formatted **Project Charter** and **Risk Register** in HTML.

## Quick Start

```bash
pip install streamlit pymupdf4llm
streamlit run app.py
```

Place the three source files in `common/input/` before clicking **Process**:

| File | Content |
|------|---------|
| `rfp_summary.md` | RFP: background, evaluation criteria |
| `business_requirements.md` | BRD: objectives, requirements, constraints |
| `purchase_order.md` | PO: contacts, deliverables, project plan, payment terms |

Outputs are written to `shared_output/`:
- `Project_Charter.html`
- `Risk_Register.html`

---

## Architecture

```
pmd-automator/
├── app.py                              # Streamlit dashboard
├── common/
│   ├── input/                          # Source documents + extracted snippets
│   ├── templates/                      # Reference templates (read-only)
│   └── validation/sow_headers.json     # Anchor schema and fallback patterns
├── agents/
│   └── initiation/
│       ├── runner.py                   # Pipeline orchestrator
│       ├── plugins/                    # Assembly plugins (see below)
│       └── skills/                     # Extraction skill definitions
├── shared_output/                      # Generated deliverables
└── state/                              # Agent state (ingestion phase)
```

### Pipeline Stages

```
Stage 1 — Pre-flight Checks
  Validates each source file exists and is non-empty before any work begins.

Stage 2 — Extraction (parallel)
  Runs 4 extraction skills concurrently via ThreadPoolExecutor:
  ├─ scope_obj          → background, objectives, functional requirements
  ├─ risks_constraints  → constraints, NFRs, evaluation criteria + Risk Register HTML
  ├─ stakeholders_gov   → contact table, governance roles
  └─ milestones_finance → deliverables, project plan, payment schedule
  Each skill writes a .md snippet to common/input/snippets/.

Stage 3 — Assembly (plugin)
  Charter HTML plugin reads the four snippets and produces Project_Charter.html.
```

---

## Recent Changes

### Pre-flight Validation Hook (`runner.py`)

A dedicated **Stage 1: Pre-flight Checks** now runs before extraction. It validates that each of the three required source files:

1. Exists in `common/input/`
2. Is non-empty (size > 0)

If any check fails, the pipeline halts immediately with a `stage_error` event listing the problematic files. Previously, only a bare existence check existed inline inside `main()` with no progress visibility in the UI.

### Charter Assembly Plugin (`agents/initiation/plugins/charter_html/`)

Charter HTML assembly has been extracted from `runner.py` into a self-contained **plugin**. The runner is now format-agnostic — it orchestrates stages but has no knowledge of how the charter is rendered.

**Plugin interface:**

```python
class CharterHtmlPlugin:
    name  = "charter_html"
    label = "HTML Assembly — Charter"

    def run(self, emit_fn, step, total, snippets_dir, output_dir) -> tuple[bool, list[str]]:
        ...
```

**Plugin registry in `runner.py`:**

```python
ASSEMBLY_PLUGINS = [
    "agents.initiation.plugins.charter_html.plugin",
]
```

To add a new output format (e.g. PDF, DOCX, Executive Summary), create a plugin under `agents/initiation/plugins/<name>/plugin.py` with a class exposing the same `run()` interface, then append its module path to `ASSEMBLY_PLUGINS`.

---

## Adding a Plugin

1. Create the module:
   ```
   agents/initiation/plugins/<your_plugin>/
   ├── __init__.py
   └── plugin.py
   ```

2. Implement the class:
   ```python
   class YourPlugin:
       name  = "<your_plugin>"
       label = "Your Plugin Label"

       def run(self, emit_fn, step, total, snippets_dir, output_dir):
           # emit stage_start, stage_done / stage_error events via emit_fn
           # read snippets from snippets_dir
           # write output to output_dir
           return success: bool, output_paths: list[str]
   ```

3. Register it:
   ```python
   # agents/initiation/runner.py
   ASSEMBLY_PLUGINS = [
       "agents.initiation.plugins.charter_html.plugin",
       "agents.initiation.plugins.<your_plugin>.plugin",
   ]
   ```

---

## Event Schema

The runner emits newline-delimited JSON to stdout, consumed by the Streamlit UI:

| Event | When |
|-------|------|
| `stage_start` | A stage begins |
| `stage_progress` | Sub-progress within a stage |
| `stage_done` | A stage completes successfully |
| `stage_error` | A stage fails (pipeline halts) |
| `stage_warning` | Non-fatal issue within a stage |
| `complete` | All stages done; includes output file paths |
