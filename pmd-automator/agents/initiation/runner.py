"""
Initiation Agent workflow runner — v3 (centralized engine).
Stages: Extraction (parallel) → HTML Assembly
Ingestion and Validation are suspended; engine reads directly from /common/input/.
Emits newline-delimited JSON events to stdout for Streamlit to consume.
"""

from __future__ import annotations

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_STDOUT    = sys.stdout
_EMIT_LOCK = Lock()

REPO_ROOT  = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "common" / "validation" / "sow_headers.json"

# ---------------------------------------------------------------------------
# Centralized paths — all source files live here, no project subdirectories
# ---------------------------------------------------------------------------
INPUT_DIR   = REPO_ROOT / "common" / "input"
OUTPUT_DIR  = REPO_ROOT / "shared_output"
OUTPUT_FILE          = OUTPUT_DIR / "Project_Charter.html"
RISK_REGISTER_FILE   = OUTPUT_DIR / "Risk_Register.html"

# Suspended stages are listed here for reference only
# SUSPENDED: ("ingestion",  "Ingestion")
# SUSPENDED: ("validation", "Validation")
STAGES = [
    ("extraction", "Extraction (parallel)"),
    ("assembly",   "HTML Assembly"),
]


# ---------------------------------------------------------------------------
# Event helpers
# ---------------------------------------------------------------------------

def emit(event: dict) -> None:
    with _EMIT_LOCK:
        print(json.dumps(event), file=_STDOUT, flush=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Shared extraction utilities
# ---------------------------------------------------------------------------

def _strip_frontmatter(content: str) -> str:
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip()
    return content


def _read_input(filename: str) -> str:
    """Read and strip front-matter from a file in /common/input/."""
    path = INPUT_DIR / filename
    if not path.exists():
        return ""
    return _strip_frontmatter(path.read_text(encoding="utf-8"))


def _extract_section(content: str, anchor_id: str, patterns: list[str]) -> str:
    """Extract a section by anchor tag, then substring heading match.

    Handles prefixed headings such as '## A. Background & Context' or
    '## 3. Functional Requirements' — the pattern only needs to appear
    *anywhere* in the heading text, not as an exact full match.
    """
    lc        = content.lower()
    open_tag  = f"<!-- anchor:{anchor_id} -->"
    close_tag = f"<!-- anchor:{anchor_id}:end -->"

    # 1. Explicit anchor tags take priority
    if open_tag in lc:
        start = lc.index(open_tag) + len(open_tag)
        if close_tag in lc[start:]:
            end = lc.index(close_tag, start)
            return content[start:end].strip()
        rest = content[start:]
        m = re.search(r"\n#{1,3} ", rest)
        return rest[: m.start()].strip() if m else rest.strip()

    # 2. Substring match against each heading line
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        hm = re.match(r'^(#{1,4})\s+(.*)', line)
        if not hm:
            continue
        heading_text = hm.group(2).strip()
        level        = len(hm.group(1))

        for pattern in patterns:
            if pattern.lower() in heading_text.lower():
                # Collect body until next heading of equal or higher level
                body_lines = [line]
                for rest_line in lines[idx + 1:]:
                    if re.match(rf'^#{{1,{level}}}\s', rest_line):
                        break
                    body_lines.append(rest_line)
                return "\n".join(body_lines).strip()

    return ""

    return ""


def _extract_labels(content: str, labels: list[str]) -> dict[str, str]:
    """Scan for **Label:** value patterns (used for governance fields)."""
    result: dict[str, str] = {}
    for label in labels:
        m = re.search(
            rf"(?m)[\*_]{{0,2}}{re.escape(label)}[\*_]{{0,2}}\s*[:：]\s*(.+)",
            content, re.IGNORECASE,
        )
        if m:
            result[label] = m.group(1).strip().strip("*_")
    return result


def _write_snippet(snippets_dir: Path, name: str, content: str) -> None:
    snippets_dir.mkdir(parents=True, exist_ok=True)
    front = f"---\nskill: {name}\nextracted_at: {_now_iso()}\n---\n\n"
    (snippets_dir / f"{name}.md").write_text(front + content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Risk Register — CSS, helpers, and HTML builder
# ---------------------------------------------------------------------------

_RISK_REGISTER_CSS = """
:root {
  --primary: #007560; --primary-variant: #004937;
  --primary-tint: #D9EAE7; --primary-tint-soft: #E5F1EF;
  --accent-orange: #E26D5A;
  --error: #B00020;
  --grey-100: #EFEFF1; --grey-150: #F2F3F3; --grey-200: #D7D7DF;
  --grey-600: #6F6F6F; --grey-700: #4D4D4D; --grey-900: #222222;
  --warn-bg: #FCF5E7; --warn-icon: #C28B14;
  --font: -apple-system, "SF Pro Display", "SF Pro Text", "Helvetica Neue", system-ui, sans-serif;
  --mono: "SF Mono", ui-monospace, Menlo, Consolas, monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font);
  font-size: 13px; color: var(--grey-900); background: #E9EAEC; line-height: 1.5;
}
.page {
  max-width: 1280px; margin: 32px auto; background: #fff;
  border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,.08), 0 8px 28px rgba(0,0,0,.10); overflow: hidden;
}
header {
  background: linear-gradient(to bottom, var(--primary) 0%, var(--primary-variant) 100%);
  color: #fff; padding: 28px 48px 22px;
}
header h1 { font-size: 22px; font-weight: 700; letter-spacing: .5px; }
header .meta { margin-top: 8px; font-size: 12px; opacity: .82; }
header .meta span { margin-right: 24px; }
.badge-draft {
  display: inline-block; background: var(--accent-orange); color: #fff;
  font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 12px;
  text-transform: uppercase; letter-spacing: .6px; margin-left: 10px;
  vertical-align: middle;
}
main { padding: 24px 32px 48px; }
.summary { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.summary-card {
  flex: 1; min-width: 120px; background: var(--grey-150);
  border: 1px solid var(--grey-200); border-radius: 6px;
  padding: 12px 16px; text-align: center;
}
.summary-card .count { font-size: 26px; font-weight: 700; color: var(--primary); }
.summary-card .label { font-size: 11px; color: var(--grey-600); text-transform: uppercase; letter-spacing: .5px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
thead { background: var(--primary); color: #fff; }
thead th { padding: 10px 12px; text-align: left; font-weight: 600; white-space: nowrap;
  font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }
tbody tr:nth-child(even) { background: #FAFAFB; }
tbody tr:hover { background: var(--primary-tint-soft); }
tbody td { padding: 8px 12px; border-bottom: 1px solid var(--grey-100); vertical-align: top; color: var(--grey-900); }
.risk-id { font-weight: 700; color: var(--primary); white-space: nowrap; font-family: var(--mono); }
.badge {
  display: inline-block; color: #fff; font-size: 10px; font-weight: 700;
  padding: 2px 8px; border-radius: 10px; text-transform: uppercase;
  letter-spacing: .5px; white-space: nowrap;
}
footer {
  background: var(--grey-150); border-top: 1px solid var(--grey-100);
  padding: 12px 32px; font-size: 11px; color: var(--grey-600);
  display: flex; justify-content: space-between;
}
@media print {
  body { background: #fff; }
  .page { box-shadow: none; margin: 0; border-radius: 0; }
  *, *::before, *::after {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}
"""

_PRIORITY_COLOR = {
    "Critical": "#B00020",   # --error
    "High":     "#E26D5A",   # --accent-orange
    "Medium":   "#C28B14",   # --warn-icon
    "Low":      "#007560",   # --primary
}

_SCORE_NUM = {"Low": 2, "Medium": 3, "High": 4}


def _risk_priority(impact: str, prob: str) -> tuple[int, str]:
    score = _SCORE_NUM.get(impact, 3) * _SCORE_NUM.get(prob, 3)
    label = ("Critical" if score >= 12 else
             "High"     if score >= 9  else
             "Medium"   if score >= 6  else "Low")
    return score, label


def _extract_bullet_items(text: str) -> list[str]:
    return [
        re.sub(r'^\s*[\*\-]\s+', '', line).strip()
        for line in text.splitlines()
        if re.match(r'^\s*[\*\-]\s+', line)
    ]


def _build_risk_register_html(constraints: str, nfr: str, eval_crit: str) -> str:
    rows: list[dict] = []
    risk_id = 1

    def add(desc: str, source: str, category: str,
            impact: str = "Medium", prob: str = "Medium",
            mitigation: str = "TBC") -> None:
        nonlocal risk_id
        score, priority = _risk_priority(impact, prob)
        rows.append({
            "id":         f"RISK-{risk_id:03d}",
            "category":   category,
            "description": desc,
            "source":     source,
            "impact":     impact,
            "probability": prob,
            "score":      score,
            "priority":   priority,
            "mitigation": mitigation,
        })
        risk_id += 1

    for item in _extract_bullet_items(constraints):
        m = re.match(r'\*{0,2}(.+?)\*{0,2}[:\s]+(.*)', item)
        label   = m.group(1).strip() if m else ""
        desc    = m.group(2).strip() if m else item
        ll      = label.lower()
        if any(k in ll for k in ["timeline", "week", "month", "deadline"]):
            add(f"{label}: {desc}", "Project Constraints", "Schedule", "High", "High",
                "Define realistic milestones; add buffer weeks at phase boundaries")
        elif any(k in ll for k in ["budget", "cost", "usd", "$"]):
            add(f"{label}: {desc}", "Project Constraints", "Budget", "High", "Medium",
                "Track spend weekly; escalate at 80% threshold")
        elif any(k in ll for k in ["parity", "platform", "ios", "android"]):
            add(f"{label}: {desc}", "Project Constraints", "Technical", "Medium", "Medium",
                "Shared business logic layer; platform-specific UI only")
        else:
            add(f"{label}: {desc}" if label else desc, "Project Constraints", "Other")

    for item in _extract_bullet_items(nfr):
        m = re.match(r'\*{0,2}(.+?)\*{0,2}[:\s]+(.*)', item)
        label = m.group(1).strip() if m else ""
        desc  = m.group(2).strip() if m else item
        ll    = label.lower()
        if any(k in ll for k in ["security", "auth", "jwt"]):
            add(f"{label}: {desc}", "Non-Functional Requirements", "Compliance/Security",
                "High", "Medium", "Enforce 80%+ test coverage gates; run SAST in CI")
        elif any(k in ll for k in ["compliance", "encrypt", "gdpr", "hipaa"]):
            add(f"{label}: {desc}", "Non-Functional Requirements", "Compliance/Security",
                "High", "Low", "Implement encryption standards; conduct compliance review pre-launch")
        elif any(k in ll for k in ["performance", "response", "latency", "api"]):
            add(f"{label}: {desc}", "Non-Functional Requirements", "Technical",
                "Medium", "Medium", "Load test at each milestone; set SLA thresholds in CI")
        else:
            add(f"{label}: {desc}" if label else desc, "Non-Functional Requirements", "Technical")

    for item in _extract_bullet_items(eval_crit):
        m = re.match(r'\*{0,2}(.+?)\*{0,2}[:\s]+(.*)', item)
        label = m.group(1).strip() if m else ""
        desc  = m.group(2).strip() if m else item
        add(f"{label}: {desc}" if label else desc, "Evaluation Criteria", "Stakeholder",
            "Medium", "Medium", "Align expectations early; schedule demo checkpoints")

    generated = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")

    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for r in rows:
        counts[r["priority"]] += 1

    summary_html = "".join(
        f'<div class="summary-card">'
        f'<div class="count" style="color:{_PRIORITY_COLOR[p]}">{counts[p]}</div>'
        f'<div class="label">{p}</div></div>'
        for p in ("Critical", "High", "Medium", "Low")
    )
    summary_html = (
        f'<div class="summary-card"><div class="count">{len(rows)}</div>'
        f'<div class="label">Total Risks</div></div>' + summary_html
    )

    rows_html = "".join(
        f'<tr>'
        f'<td class="risk-id">{r["id"]}</td>'
        f'<td>{r["category"]}</td>'
        f'<td>{r["description"]}</td>'
        f'<td>{r["source"]}</td>'
        f'<td>{r["impact"]}</td>'
        f'<td>{r["probability"]}</td>'
        f'<td style="text-align:center;font-weight:700">{r["score"]}</td>'
        f'<td><span class="badge" style="background:{_PRIORITY_COLOR[r["priority"]]}">'
        f'{r["priority"]}</span></td>'
        f'<td>{r["mitigation"]}</td>'
        f'</tr>'
        for r in rows
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>High-Level Risk Register</title>
  <style>{_RISK_REGISTER_CSS}</style>
</head>
<body>
  <div class="page">
    <header>
      <h1>High-Level Risk Register<span class="badge-draft">Draft</span></h1>
      <div class="meta">
        <span>📋 PMO Automator</span>
        <span>📅 {generated}</span>
        <span>👤 Riyaz Kallayimmel, PMP</span>
      </div>
    </header>
    <main>
      <div class="summary">{summary_html}</div>
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th>Risk ID</th><th>Category</th><th>Risk Description</th><th>Source</th>
            <th>Impact</th><th>Probability</th><th>Score</th><th>Priority</th><th>Mitigation</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </main>
    <footer>
      <span>PMO Automator — High-Level Risk Register (extract-risks-constraints v3)</span>
      <span>Generated {generated}</span>
    </footer>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# SUSPENDED — Stage 1: Ingestion (PDF → Markdown)
# ---------------------------------------------------------------------------
# def run_ingestion(project_root: Path, state_path: Path) -> bool:
#     """Convert PDFs in 00_inbox/ to Markdown in 02_working_docs/."""
#     ...
#     # SUSPENDED: engine now reads directly from /common/input/
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# SUSPENDED — Stage 2: Validation (schema/anchor completeness check)
# ---------------------------------------------------------------------------
# def run_validation(project_root: Path) -> bool:
#     """Validate that all required anchors exist in working documents."""
#     ...
#     # SUSPENDED: engine proceeds directly to extraction
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Stage 1 (of 2) — Extraction: 4 parallel skills reading from /common/input/
# ---------------------------------------------------------------------------

def _skill_scope_obj(schema: dict, snippets_dir: Path) -> tuple[str, str]:
    """Extract background, objectives, functional requirements."""
    rf  = schema["required_files"]
    rfp = _read_input("rfp_summary.md")
    brd = _read_input("business_requirements.md")

    bg  = _extract_section(rfp, "background",
                            rf["rfp_summary.md"]["fallback_patterns"]["background"])
    obj = _extract_section(brd, "business_objective",
                            rf["business_requirements.md"]["fallback_patterns"]["business_objective"])
    frs = _extract_section(brd, "functional_requirements",
                            rf["business_requirements.md"]["fallback_patterns"]["functional_requirements"])

    content = "\n\n".join([
        "## 2. Project Purpose & Business Case\n\n"
        + (bg  or "<!-- NOT_FOUND: background -->"),
        "## 3. Project Objectives & Success Criteria\n\n"
        + (obj or "<!-- NOT_FOUND: business_objective -->"),
        "## 4. High-Level Requirements\n\n"
        + (frs or "<!-- NOT_FOUND: functional_requirements -->"),
    ])
    _write_snippet(snippets_dir, "scope_obj", content)
    return "scope_obj", content


def _skill_risks_constraints(schema: dict, snippets_dir: Path) -> tuple[str, str]:
    """Extract constraints, NFRs, and evaluation criteria as risks."""
    rf  = schema["required_files"]
    brd = _read_input("business_requirements.md")
    rfp = _read_input("rfp_summary.md")

    constraints = _extract_section(
        brd, "project_constraints",
        rf["business_requirements.md"]["fallback_patterns"]["project_constraints"])
    nfr = _extract_section(
        brd, "non_functional_requirements",
        rf["business_requirements.md"]["fallback_patterns"]["non_functional_requirements"])
    eval_crit = _extract_section(
        rfp, "evaluation_criteria",
        rf["rfp_summary.md"]["fallback_patterns"]["evaluation_criteria"])

    content = "\n\n".join([
        "## 6. Risks, Assumptions & Constraints",
        "### 6a. Project Constraints\n\n"
        + (constraints or "<!-- NOT_FOUND: project_constraints -->"),
        "### 6b. Non-Functional Requirements & Derived Risks\n\n"
        + (nfr        or "<!-- NOT_FOUND: non_functional_requirements -->"),
        "### 6c. Evaluation Criteria Cross-Reference\n\n"
        + (eval_crit  or "<!-- NOT_FOUND: evaluation_criteria -->"),
        "### 6d. Assumptions\n\n- TBC — to be completed by the Project Manager.",
    ])
    _write_snippet(snippets_dir, "risks_constraints", content)

    # Also produce a standalone risk register HTML
    rr_html = _build_risk_register_html(constraints, nfr, eval_crit)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RISK_REGISTER_FILE.write_text(rr_html, encoding="utf-8")

    return "risks_constraints", content


def _skill_stakeholders_gov(schema: dict, snippets_dir: Path) -> tuple[str, str]:
    """Extract contact table and governance roles."""
    rf  = schema["required_files"]
    gov = schema.get("governance_fields", {})
    po  = _read_input("purchase_order.md")
    brd = _read_input("business_requirements.md")

    contacts = _extract_section(
        po, "contact_information",
        rf["purchase_order.md"]["fallback_patterns"]["contact_information"])
    labels   = gov.get("labels", ["Author", "Prepared By", "Stakeholder Lead"])
    gov_data = _extract_labels(brd, labels)
    role_map : dict = gov.get("role_mapping", {})
    gov_lines = [f"- **{role_map.get(lbl, lbl)}:** {val}"
                 for lbl, val in gov_data.items()]

    content = "\n\n".join([
        "## 7. Governance & Authority",
        "### 7a. Stakeholder Register\n\n"
        + (contacts or "<!-- NOT_FOUND: contact_information -->"),
        "### 7b. Governance Roles\n\n"
        + ("\n".join(gov_lines) if gov_lines else "<!-- NOT_FOUND: governance_fields -->"),
    ])
    _write_snippet(snippets_dir, "stakeholders_gov", content)
    return "stakeholders_gov", content


def _skill_milestones_finance(schema: dict, snippets_dir: Path) -> tuple[str, str]:
    """Extract deliverables, project plan, and payment terms."""
    rf = schema["required_files"]
    po = _read_input("purchase_order.md")

    deliverables = _extract_section(
        po, "key_deliverables",
        rf["purchase_order.md"]["fallback_patterns"]["key_deliverables"])
    plan = _extract_section(
        po, "project_plan",
        rf["purchase_order.md"]["fallback_patterns"]["project_plan"])
    payment = _extract_section(
        po, "payment_terms",
        rf["purchase_order.md"]["fallback_patterns"]["payment_terms"])

    content = "\n\n".join([
        "## 5. Summary Milestone Schedule & Payment Terms",
        "### 5a. Deliverable Register\n\n"
        + (deliverables or "<!-- NOT_FOUND: key_deliverables -->"),
        "### 5b. Project Plan Phases\n\n"
        + (plan         or "<!-- NOT_FOUND: project_plan -->"),
        "### 5c. Payment Schedule\n\n"
        + (payment      or "<!-- NOT_FOUND: payment_terms -->"),
    ])
    _write_snippet(snippets_dir, "milestones_finance", content)
    return "milestones_finance", content


def run_extraction() -> bool:
    step, total = 1, len(STAGES)
    emit({"event": "stage_start", "stage": "extraction",
          "label": "Extraction (parallel)", "step": step, "total": total,
          "ts": _now_iso()})
    try:
        schema       = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        snippets_dir = INPUT_DIR / "snippets"

        skills = {
            "scope_obj":          lambda: _skill_scope_obj(schema, snippets_dir),
            "risks_constraints":  lambda: _skill_risks_constraints(schema, snippets_dir),
            "stakeholders_gov":   lambda: _skill_stakeholders_gov(schema, snippets_dir),
            "milestones_finance": lambda: _skill_milestones_finance(schema, snippets_dir),
        }

        completed = 0
        errors: list[str] = []

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(fn): name for name, fn in skills.items()}
            for future in as_completed(futures):
                name = futures[future]
                completed += 1
                try:
                    future.result()
                    emit({
                        "event": "stage_progress", "stage": "extraction",
                        "step": step, "total": total,
                        "sub_pct": completed / len(skills),
                        "label": f"Extracted: {name} ({completed}/{len(skills)})",
                        "ts": _now_iso(),
                    })
                except Exception as exc:
                    errors.append(f"{name}: {exc}")
                    emit({"event": "stage_warning",
                          "detail": f"Skill '{name}' failed: {exc}", "ts": _now_iso()})

        if len(errors) == len(skills):
            emit({"event": "stage_error", "stage": "extraction",
                  "step": step, "total": total,
                  "error": "All extraction skills failed", "ts": _now_iso()})
            return False

        emit({"event": "stage_done", "stage": "extraction",
              "step": step, "total": total, "ts": _now_iso()})
        return True

    except Exception as exc:
        emit({"event": "stage_error", "stage": "extraction",
              "step": step, "total": total, "error": str(exc), "ts": _now_iso()})
        return False


# ---------------------------------------------------------------------------
# Markdown → HTML converter
# ---------------------------------------------------------------------------

def _inline(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*',     r'<em>\1</em>',         text)
    text = re.sub(r'`(.*?)`',       r'<code>\1</code>',     text)
    return text


def _md_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # NOT_FOUND placeholders → amber warning box
        if line.strip().startswith("<!--") and "NOT_FOUND" in line:
            field = re.search(r"NOT_FOUND:\s*(\w+)", line)
            label = field.group(1).replace("_", " ").title() if field else "Section"
            out.append(
                f'<div class="not-found">⚠ {label} — '
                f'not found in source documents. Requires manual entry.</div>'
            )
            i += 1
            continue

        if line.strip().startswith("<!--"):
            i += 1
            continue

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            lvl  = len(m.group(1))
            text = _inline(m.group(2))
            cls  = "section-heading" if lvl == 2 else ("sub-heading" if lvl == 3 else "")
            out.append(f'<h{lvl} class="{cls}">{text}</h{lvl}>')
            i += 1
            continue

        # Tables
        if line.strip().startswith("|") and "|" in line:
            rows: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            if not rows:
                continue
            out.append('<div class="table-wrap"><table>')
            header = [c.strip() for c in rows[0].strip().strip("|").split("|")]
            out.append("<thead><tr>"
                       + "".join(f"<th>{_inline(c)}</th>" for c in header)
                       + "</tr></thead><tbody>")
            for row in rows[1:]:
                if re.match(r"^[\|\s\-:]+$", row):
                    continue
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                out.append("<tr>"
                           + "".join(f"<td>{_inline(c)}</td>" for c in cells)
                           + "</tr>")
            out.append("</tbody></table></div>")
            continue

        # Bullet lists
        if re.match(r"^[\*\-]\s+", line):
            out.append("<ul>")
            while i < len(lines) and re.match(r"^[\*\-]\s+", lines[i]):
                out.append(f"<li>{_inline(lines[i][2:].strip())}</li>")
                i += 1
            out.append("</ul>")
            continue

        # Numbered lists
        if re.match(r"^\d+\.\s+", line):
            out.append("<ol>")
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                out.append(f"<li>{_inline(re.sub(r'^\\d+\\.\\s+', '', lines[i]))}</li>")
                i += 1
            out.append("</ol>")
            continue

        if not line.strip():
            i += 1
            continue

        out.append(f"<p>{_inline(line)}</p>")
        i += 1

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Stage 2 (of 2) — HTML Assembly → /shared_output/Project_Charter.html
# ---------------------------------------------------------------------------

_CSS = """
:root {
  --primary: #007560; --primary-variant: #004937;
  --primary-tint: #D9EAE7; --primary-tint-soft: #E5F1EF;
  --accent-orange: #E26D5A;
  --grey-100: #EFEFF1; --grey-150: #F2F3F3; --grey-200: #D7D7DF;
  --grey-300: #BDBDBD; --grey-600: #6F6F6F; --grey-900: #222222;
  --warn-bg: #FCF5E7; --warn-border: #C28B14; --warn-text: #7B5A0F;
  --font: -apple-system, "SF Pro Display", "SF Pro Text", "Helvetica Neue", system-ui, sans-serif;
  --mono: "SF Mono", ui-monospace, Menlo, Consolas, monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font);
  font-size: 14px; color: var(--grey-900); background: #E9EAEC; line-height: 1.65;
}
.page {
  max-width: 960px; margin: 32px auto; background: #fff;
  border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,.08), 0 8px 28px rgba(0,0,0,.10); overflow: hidden;
}
header {
  background: linear-gradient(to bottom, var(--primary) 0%, var(--primary-variant) 100%);
  color: #fff; padding: 36px 48px 28px;
}
header h1 { font-size: 26px; font-weight: 700; letter-spacing: .5px; }
header .meta { margin-top: 10px; font-size: 13px; opacity: .82; }
header .meta span { margin-right: 24px; }
.badge {
  display: inline-block; background: var(--accent-orange); color: #fff;
  font-size: 11px; font-weight: 700; padding: 2px 10px; border-radius: 12px;
  text-transform: uppercase; letter-spacing: .6px; margin-left: 10px;
  vertical-align: middle;
}
main { padding: 0 48px 48px; }
.section-card {
  margin-top: 32px; border: 1px solid var(--grey-200); border-radius: 6px; overflow: hidden;
}
.section-title {
  background: var(--primary); color: #fff; padding: 10px 20px;
  font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .8px;
}
.section-body { padding: 20px 24px; }
h2.section-heading { display: none; }
h3.sub-heading {
  font-size: 13px; font-weight: 700; color: var(--primary);
  margin: 18px 0 8px; padding-bottom: 4px; border-bottom: 1px solid var(--grey-100);
}
p { margin: 6px 0; }
ul, ol { margin: 6px 0 6px 20px; }
li { margin: 3px 0; }
.table-wrap { overflow-x: auto; margin: 10px 0; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead { background: var(--primary); color: #fff; }
thead th { padding: 8px 12px; text-align: left; font-weight: 600;
  font-size: 12px; letter-spacing: .06em; text-transform: uppercase; }
tbody tr:nth-child(even) { background: #FAFAFB; }
tbody td { padding: 7px 12px; border-bottom: 1px solid var(--grey-100); }
code { background: var(--grey-150); padding: 1px 5px; border-radius: 3px; font-size: 12px; font-family: var(--mono); }
strong { font-weight: 700; }
.not-found {
  background: var(--warn-bg); border-left: 4px solid var(--warn-border);
  padding: 10px 14px; font-size: 13px; color: var(--warn-text);
  border-radius: 0 4px 4px 0; margin: 8px 0;
}
.sign-off-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 8px; }
.sign-box { border: 1px solid var(--grey-200); border-radius: 4px; padding: 16px; }
.sign-box .role {
  font-weight: 700; font-size: 12px; color: var(--primary);
  text-transform: uppercase; letter-spacing: .5px;
}
.sign-box .name { margin: 4px 0 20px; font-size: 14px; }
.sign-line {
  border-top: 1px solid var(--grey-300); margin-top: 20px;
  font-size: 11px; color: var(--grey-600); padding-top: 4px;
}
footer {
  background: var(--grey-150); border-top: 1px solid var(--grey-100);
  padding: 14px 48px; font-size: 11px; color: var(--grey-600);
  display: flex; justify-content: space-between;
}
@media print {
  body { background: #fff; }
  .page { box-shadow: none; margin: 0; border-radius: 0; }
  *, *::before, *::after {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}
"""


def _section_card(title: str, content_md: str) -> str:
    return (
        f'<div class="section-card">'
        f'<div class="section-title">{title}</div>'
        f'<div class="section-body">{_md_to_html(content_md)}</div>'
        f'</div>'
    )


def _build_html(snippets: dict[str, str]) -> str:
    generated = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")

    overview_md = f"""
| Field | Value |
|-------|-------|
| **Document** | Project Charter |
| **Status** | DRAFT — Pending Approval |
| **Version** | v1 |
| **Generated** | {generated} |
| **Prepared by** | Riyaz Kallayimmel, PMP |
""".strip()

    sign_off_html = """
<div class="sign-off-grid">
  <div class="sign-box">
    <div class="role">Project Sponsor</div>
    <div class="name">&nbsp;</div>
    <div class="sign-line">Signature &amp; Date</div>
  </div>
  <div class="sign-box">
    <div class="role">Project Manager</div>
    <div class="name">Riyaz Kallayimmel, PMP</div>
    <div class="sign-line">Signature &amp; Date</div>
  </div>
</div>
<p style="margin-top:14px;font-size:12px;color:#64748b;">
  By signing above, the parties confirm that this Project Charter accurately
  represents the agreed scope, objectives, and governance for the project.
</p>
"""

    body = "".join([
        _section_card("1. Project Overview", overview_md),
        _section_card("2–4. Scope, Objectives & Requirements",
                      snippets.get("scope_obj", "")),
        _section_card("5. Milestone Schedule & Payment Terms",
                      snippets.get("milestones_finance", "")),
        _section_card("6. Risks, Assumptions & Constraints",
                      snippets.get("risks_constraints", "")),
        _section_card("7. Governance & Authority",
                      snippets.get("stakeholders_gov", "")),
        (
            '<div class="section-card">'
            '<div class="section-title">8. Approval &amp; Sign-off</div>'
            f'<div class="section-body">{sign_off_html}</div>'
            '</div>'
        ),
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Project Charter</title>
  <style>{_CSS}</style>
</head>
<body>
  <div class="page">
    <header>
      <h1>Project Charter<span class="badge">Draft</span></h1>
      <div class="meta">
        <span>📋 PMO Automator</span>
        <span>📅 {generated}</span>
        <span>👤 Riyaz Kallayimmel, PMP</span>
      </div>
    </header>
    <main>{body}</main>
    <footer>
      <span>PMO Automator — Centralized Initiation Engine v3</span>
      <span>Generated {generated}</span>
    </footer>
  </div>
</body>
</html>"""


def run_assembly() -> tuple[bool, str]:
    step, total = 2, len(STAGES)
    emit({"event": "stage_start", "stage": "assembly", "label": "HTML Assembly",
          "step": step, "total": total, "ts": _now_iso()})
    try:
        snippets_dir = INPUT_DIR / "snippets"
        snippets: dict[str, str] = {}

        for name in ("scope_obj", "milestones_finance", "risks_constraints", "stakeholders_gov"):
            path = snippets_dir / f"{name}.md"
            if path.exists():
                snippets[name] = _strip_frontmatter(path.read_text(encoding="utf-8"))
            else:
                snippets[name] = f"<!-- NOT_FOUND: {name} -->"

        html = _build_html(snippets)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(html, encoding="utf-8")
        html_path = str(OUTPUT_FILE)

        rr_path = str(RISK_REGISTER_FILE) if RISK_REGISTER_FILE.exists() else ""
        outputs = [html_path] + ([rr_path] if rr_path else [])
        emit({"event": "stage_done", "stage": "assembly",
              "step": step, "total": total, "outputs": outputs, "ts": _now_iso()})
        emit({"event": "complete", "html_path": html_path,
              "risk_register_path": rr_path, "outputs": outputs, "ts": _now_iso()})
        return True, html_path

    except Exception as exc:
        emit({"event": "stage_error", "stage": "assembly",
              "step": step, "total": total, "error": str(exc), "ts": _now_iso()})
        return False, ""


# ---------------------------------------------------------------------------
# Entrypoint — no project args required; reads from /common/input/
# ---------------------------------------------------------------------------

def main() -> int:
    # Validate that /common/input/ has the required files before starting
    missing = [f for f in
               ("rfp_summary.md", "business_requirements.md", "purchase_order.md")
               if not (INPUT_DIR / f).exists()]
    if missing:
        emit({"event": "stage_error", "stage": "extraction", "step": 1, "total": 2,
              "error": f"Missing in {INPUT_DIR.name}/: {', '.join(missing)}",
              "ts": _now_iso()})
        return 1

    # SUSPENDED: run_ingestion(...)   # PDF → Markdown
    # SUSPENDED: run_validation(...)  # Schema / anchor checks

    if not run_extraction():
        return 1

    success, _ = run_assembly()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
