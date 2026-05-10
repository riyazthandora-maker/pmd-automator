"""PMO Automator — Streamlit dashboard."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="PMO Automator",
    page_icon="📋",
    layout="wide",
)

st.title("📋 PMO Automator")
st.caption("Initiation Agent — automated charter generation pipeline")

# ---------------------------------------------------------------------------
# Load registry
# ---------------------------------------------------------------------------

registry_path = ROOT / "projects_registry.json"
if not registry_path.exists():
    st.error("`projects_registry.json` not found in project root.")
    st.stop()

try:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    projects: list[dict] = registry.get("projects", [])
except json.JSONDecodeError as exc:
    st.error(f"Failed to parse `projects_registry.json`: {exc}")
    st.stop()

# ---------------------------------------------------------------------------
# Status badge helper
# ---------------------------------------------------------------------------

_STATUS_COLOR = {
    "Initiation": "orange",
    "Planning": "blue",
    "In Progress": "blue",
    "Complete": "green",
    "On Hold": "red",
    "Cancelled": "gray",
}


def _badge(status: str) -> str:
    color = _STATUS_COLOR.get(status, "gray")
    return f":{color}[{status}]"


# ---------------------------------------------------------------------------
# Project registry table
# ---------------------------------------------------------------------------

st.subheader("Project Registry")

col_refresh = st.columns([10, 1])[1]
if col_refresh.button("↺ Refresh"):
    st.rerun()

if not projects:
    st.info("No projects found in `projects_registry.json`.")
else:
    # Header row
    h = st.columns([3, 3, 1.5, 1.5, 1.8, 2])
    for col, label in zip(h, ["**Project**", "**Description**", "**Lead**",
                               "**Start Date**", "**Status**", "**Action**"]):
        col.markdown(label)
    st.divider()

    for project in projects:
        pid = project.get("id", "")
        status = project.get("status", "Unknown")

        row = st.columns([3, 3, 1.5, 1.5, 1.8, 2])
        row[0].markdown(f"**{project.get('name', pid)}**")
        row[1].write(project.get("description", "—"))
        row[2].write(project.get("lead", "—"))
        row[3].write(project.get("start_date", "—"))
        row[4].markdown(_badge(status))

        if status == "Initiation":
            already_processing = st.session_state.get("active_project") == pid
            btn_label = "⏳ Running…" if already_processing else "▶ Process"
            if row[5].button(btn_label, key=f"btn_{pid}", disabled=already_processing):
                st.session_state["active_project"] = pid
                st.session_state.pop("result", None)
                st.rerun()
        else:
            row[5].write("—")

# ---------------------------------------------------------------------------
# Processing panel
# ---------------------------------------------------------------------------

if "active_project" not in st.session_state:
    st.stop()

project_id: str = st.session_state["active_project"]
project = next((p for p in projects if p["id"] == project_id), None)

if project is None:
    st.error(f"Project `{project_id}` not found in registry.")
    del st.session_state["active_project"]
    st.stop()

st.divider()

panel_col, close_col = st.columns([9, 1])
panel_col.subheader(f"Processing: {project['name']}")
if close_col.button("✕ Close", key="close_panel"):
    del st.session_state["active_project"]
    st.session_state.pop("result", None)
    st.rerun()

# If we already have a cached result (subprocess finished), just display it
if "result" in st.session_state:
    res = st.session_state["result"]
    if res.get("validation_failed"):
        missing = res["missing_headers"]
        bullet_list = "\n".join(f"- `{m}`" for m in missing)
        st.error(
            "### Validation Failed\n\n"
            "The following required SOW sections are missing from the working document. "
            "Add these headings (or anchor tags) to your document and re-process.\n\n"
            + bullet_list
        )
    elif res.get("success"):
        outputs = res.get("outputs", [])
        out_str = "\n".join(f"- `{o}`" for o in outputs) if outputs else ""
        st.success(
            f"Processing complete! Charter saved to `04_final_deliverables/`.\n\n{out_str}"
        )
    else:
        st.error(f"Processing failed (exit code {res.get('returncode', '?')}).")
    st.stop()

STAGES_LABELS: dict[str, str] = {
    "ingestion":  "Ingestion",
    "validation": "Validation",
    "extraction": "Extraction",
    "assembly":   "Assembly",
}

# ---------------------------------------------------------------------------
# Run the subprocess and stream events
# ---------------------------------------------------------------------------

progress_bar = st.progress(0.0, text="Initialising…")
status_box = st.empty()
log_expander = st.expander("View log", expanded=False)
log_lines: list[str] = []
log_placeholder = log_expander.empty()

runner_path = ROOT / "agents" / "initiation" / "runner.py"
project_root = ROOT / "projects" / project_id
state_path = ROOT / "state" / f"{project_id}_state.json"

proc = subprocess.Popen(
    [
        sys.executable, str(runner_path),
        "--project-id", project_id,
        "--project-root", str(project_root),
        "--state", str(state_path),
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=str(ROOT),
)

validation_failed = False
missing_headers: list[str] = []
output_paths: list[str] = []

assert proc.stdout is not None
for raw in proc.stdout:
    line = raw.strip()
    if not line:
        continue

    try:
        evt = json.loads(line)
    except json.JSONDecodeError:
        log_lines.append(line)
        log_placeholder.code("\n".join(log_lines[-15:]))
        continue

    etype = evt.get("event", "")

    if etype == "stage_start":
        step: int = evt["step"]
        total: int = evt["total"]
        label: str = evt["label"]
        pct = (step - 1) / total
        progress_bar.progress(pct, text=f"Step {step}/{total} — {label}")
        status_box.info(f"Running: **{label}**")
        log_lines.append(f"[{step}/{total}] START  {label}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    elif etype == "stage_progress":
        step = evt["step"]
        total = evt["total"]
        sub_pct: float = evt.get("sub_pct", 0.0)
        pct = min((step - 1 + sub_pct) / total, (step / total) - 0.001)
        label = evt.get("label", "")
        progress_bar.progress(pct, text=label)

    elif etype == "stage_done":
        step = evt["step"]
        total = evt["total"]
        label_done = STAGES_LABELS.get(evt.get("stage", ""), evt.get("stage", ""))
        progress_bar.progress(step / total, text=f"Step {step}/{total} — done")
        extra = ""
        if "docs_ingested" in evt:
            extra = f" ({evt['docs_ingested']} doc(s) ingested)"
        if "outputs" in evt:
            output_paths = evt["outputs"]
        log_lines.append(f"[{step}/{total}] DONE   {evt.get('stage', '')}{extra}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    elif etype == "stage_error":
        step = evt.get("step", "?")
        total = evt.get("total", "?")
        error_msg = evt.get("error", "Unknown error")
        status_box.error(f"Error in **{evt.get('stage', '?')}**: {error_msg}")
        log_lines.append(f"[{step}/{total}] ERROR  {error_msg}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    elif etype == "validation_error":
        validation_failed = True
        missing_headers = evt.get("missing", [])
        log_lines.append(f"       VALIDATION FAILED — missing: {', '.join(missing_headers)}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    elif etype == "complete":
        output_paths = evt.get("outputs", output_paths)
        progress_bar.progress(1.0, text="Complete!")
        status_box.success("Pipeline complete!")

proc.wait()

# Capture any stderr for the log
stderr_output = proc.stderr.read() if proc.stderr else ""
if stderr_output.strip():
    log_lines.append("--- stderr ---")
    log_lines.extend(stderr_output.strip().splitlines()[-20:])
    log_placeholder.code("\n".join(log_lines[-30:]))

# Cache result so closing/reopening panel doesn't re-run the subprocess
if validation_failed:
    st.session_state["result"] = {
        "validation_failed": True,
        "missing_headers": missing_headers,
    }
    missing_bullets = "\n".join(f"- `{m}`" for m in missing_headers)
    st.error(
        "### Validation Failed\n\n"
        "The following required SOW sections are **missing** from the working document. "
        "Add these headings (or `<!-- anchor:X -->` tags) and re-process.\n\n"
        + missing_bullets
    )
elif proc.returncode == 0:
    st.session_state["result"] = {"success": True, "outputs": output_paths}
    out_str = "\n".join(f"- `{o}`" for o in output_paths) if output_paths else ""
    st.success(
        f"✅ **{project['name']}** processed successfully! "
        f"Charter saved to `04_final_deliverables/`.\n\n{out_str}"
    )
else:
    st.session_state["result"] = {"success": False, "returncode": proc.returncode}
    st.error(f"Processing failed with exit code `{proc.returncode}`.")


