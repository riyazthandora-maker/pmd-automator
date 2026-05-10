"""PMO Automator — Streamlit dashboard v3 (centralized engine)."""

from __future__ import annotations

import json
import subprocess
import sys
import webbrowser
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# Centralized paths
# ---------------------------------------------------------------------------
INPUT_DIR   = ROOT / "common" / "input"
OUTPUT_FILE = ROOT / "shared_output" / "Project_Charter.html"

st.set_page_config(
    page_title="PMO Automator",
    page_icon="📋",
    layout="wide",
)

st.title("📋 PMO Automator")
st.caption("Centralized Initiation Engine · Riyaz Kallayimmel, PMP")

# ---------------------------------------------------------------------------
# Input file status panel
# ---------------------------------------------------------------------------

REQUIRED_FILES = [
    "rfp_summary.md",
    "business_requirements.md",
    "purchase_order.md",
]

st.subheader("Input Files")
st.caption(f"Source: `{INPUT_DIR.relative_to(ROOT)}`")

all_present = True
cols = st.columns(len(REQUIRED_FILES))
for col, fname in zip(cols, REQUIRED_FILES):
    exists = (INPUT_DIR / fname).exists()
    if exists:
        col.success(f"✔ `{fname}`")
    else:
        col.error(f"✘ `{fname}` missing")
        all_present = False

st.divider()

# ---------------------------------------------------------------------------
# Process button — triggers engine immediately against /common/input/
# ---------------------------------------------------------------------------

already_running = st.session_state.get("running", False)

col_btn, col_open = st.columns([2, 8])

with col_btn:
    process_clicked = st.button(
        "⏳ Running…" if already_running else "▶ Process",
        disabled=already_running or not all_present,
        use_container_width=True,
    )

with col_open:
    if OUTPUT_FILE.exists():
        if st.button("📄 Open Last Charter", use_container_width=False):
            webbrowser.open(OUTPUT_FILE.as_uri())

if not all_present:
    st.warning(
        f"Place `rfp_summary.md`, `business_requirements.md`, and "
        f"`purchase_order.md` in `{INPUT_DIR.relative_to(ROOT)}` before processing."
    )

if process_clicked:
    st.session_state["running"] = True
    st.session_state.pop("result", None)
    st.rerun()

# ---------------------------------------------------------------------------
# Show cached result without re-running
# ---------------------------------------------------------------------------

if "result" in st.session_state and not already_running:
    res = st.session_state["result"]

    if res.get("validation_failed"):
        missing = res.get("missing_headers", [])
        st.error("### ❌ Validation Failed")
        for item in missing:
            st.markdown(f"- {item}")

    elif res.get("success"):
        html_path = res.get("html_path", "")
        st.success("✅ Charter generated successfully!")
        if html_path and Path(html_path).exists():
            c1, c2 = st.columns([5, 1])
            c1.code(html_path)
            if c2.button("🌐 Open", key="open_cached"):
                webbrowser.open(Path(html_path).as_uri())
    else:
        st.error(f"Processing failed (exit code {res.get('returncode', '?')}).")

    st.stop()

if not already_running:
    st.stop()

# ---------------------------------------------------------------------------
# Run the engine subprocess and stream events
# ---------------------------------------------------------------------------

# NOTE: Ingestion (PDF→MD) and Validation (schema check) are suspended.
# The engine runs directly against /common/input/ files.
STAGE_LABELS = {
    # "ingestion":  "Ingestion",    # SUSPENDED
    # "validation": "Validation",   # SUSPENDED
    "extraction": "Extraction (parallel)",
    "assembly":   "HTML Assembly",
}
TOTAL_STAGES = len(STAGE_LABELS)

progress_bar    = st.progress(0.0, text="Starting engine…")
status_box      = st.empty()
log_expander    = st.expander("Engine log", expanded=False)
log_lines: list[str] = []
log_placeholder = log_expander.empty()

runner_path = ROOT / "agents" / "initiation" / "runner.py"

proc = subprocess.Popen(
    [sys.executable, str(runner_path)],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=str(ROOT),
)

# validation_failed = False   # SUSPENDED — validation not run
missing_headers: list[str] = []
html_path = ""

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
        step: int  = evt["step"]
        total: int = evt["total"]
        lbl: str   = evt["label"]
        pct = (step - 1) / total
        progress_bar.progress(pct, text=f"Step {step}/{total} — {lbl}")
        status_box.info(f"▶ **{lbl}**")
        log_lines.append(f"[{step}/{total}] START  {lbl}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    elif etype == "stage_progress":
        step      = evt["step"]
        total     = evt["total"]
        sub_pct: float = evt.get("sub_pct", 0.0)
        pct = min((step - 1 + sub_pct) / total, step / total - 0.001)
        lbl = evt.get("label", "")
        progress_bar.progress(pct, text=lbl)
        log_lines.append(f"         {lbl}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    elif etype == "stage_done":
        step  = evt["step"]
        total = evt["total"]
        stage = evt.get("stage", "")
        for o in evt.get("outputs", []):
            if o.endswith(".html"):
                html_path = o
        progress_bar.progress(step / total, text=f"Step {step}/{total} — done")
        status_box.success(f"✔ **{STAGE_LABELS.get(stage, stage)}** complete")
        log_lines.append(f"[{step}/{total}] DONE   {stage}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    elif etype == "stage_error":
        step  = evt.get("step", "?")
        total = evt.get("total", "?")
        msg   = evt.get("error", "Unknown error")
        status_box.error(f"❌ **{evt.get('stage', '?')}**: {msg}")
        log_lines.append(f"[{step}/{total}] ERROR  {msg}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    elif etype == "stage_warning":
        log_lines.append(f"       WARN   {evt.get('detail', '')}")
        log_placeholder.code("\n".join(log_lines[-15:]))

    # ── SUSPENDED ──────────────────────────────────────────────────────────
    # elif etype == "validation_error":
    #     validation_failed = True
    #     missing_headers = evt.get("missing", [])
    #     log_lines.append(f"       VALIDATION FAILED — {len(missing_headers)} issue(s)")
    #     log_placeholder.code("\n".join(log_lines[-15:]))
    # ── END SUSPENDED ───────────────────────────────────────────────────────

    elif etype == "complete":
        if "html_path" in evt:
            html_path = evt["html_path"]
        elif "outputs" in evt:
            for o in evt["outputs"]:
                if o.endswith(".html"):
                    html_path = o
        progress_bar.progress(1.0, text="✅ Complete!")
        status_box.success("Charter generated!")

proc.wait()

stderr_out = proc.stderr.read() if proc.stderr else ""
if stderr_out.strip():
    log_lines.append("--- stderr ---")
    log_lines.extend(stderr_out.strip().splitlines()[-20:])
    log_placeholder.code("\n".join(log_lines[-30:]))

# ---------------------------------------------------------------------------
# Final result + cache
# ---------------------------------------------------------------------------

st.session_state["running"] = False

if proc.returncode == 0:
    st.session_state["result"] = {"success": True, "html_path": html_path}
    st.success("✅ Charter generated successfully!")

    if html_path and Path(html_path).exists():
        c1, c2 = st.columns([5, 1])
        c1.code(html_path)
        if c2.button("🌐 Open in Browser", key="open_new"):
            webbrowser.open(Path(html_path).as_uri())
        webbrowser.open(Path(html_path).as_uri())
    else:
        st.warning(f"Expected output not found at: {OUTPUT_FILE}")
else:
    st.session_state["result"] = {"success": False, "returncode": proc.returncode}
    st.error(f"Processing failed with exit code `{proc.returncode}`.")
