"""Charter HTML assembly plugin — converts snippet .md files into Project_Charter.html."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

NAME  = "charter_html"
LABEL = "HTML Assembly — Charter"

_SNIPPET_NAMES = ("scope_obj", "milestones_finance", "risks_constraints", "stakeholders_gov")
_OUTPUT_FILENAME = "Project_Charter.html"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strip_frontmatter(content: str) -> str:
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip()
    return content


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
# HTML builder
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


# ---------------------------------------------------------------------------
# Plugin class
# ---------------------------------------------------------------------------

class CharterHtmlPlugin:
    name  = NAME
    label = LABEL

    def run(
        self,
        emit_fn: Callable,
        step: int,
        total: int,
        snippets_dir: Path,
        output_dir: Path,
    ) -> tuple[bool, list[str]]:
        emit_fn({"event": "stage_start", "stage": "assembly", "label": self.label,
                 "step": step, "total": total, "ts": _now_iso()})
        try:
            snippets: dict[str, str] = {}
            for name in _SNIPPET_NAMES:
                path = snippets_dir / f"{name}.md"
                if path.exists():
                    snippets[name] = _strip_frontmatter(path.read_text(encoding="utf-8"))
                else:
                    snippets[name] = f"<!-- NOT_FOUND: {name} -->"

            html = _build_html(snippets)

            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / _OUTPUT_FILENAME
            output_file.write_text(html, encoding="utf-8")
            html_path = str(output_file)

            rr_path = str(output_dir / "Risk_Register.html") \
                if (output_dir / "Risk_Register.html").exists() else ""
            outputs = [html_path] + ([rr_path] if rr_path else [])

            emit_fn({"event": "stage_done", "stage": "assembly",
                     "step": step, "total": total, "outputs": outputs, "ts": _now_iso()})
            emit_fn({"event": "complete", "html_path": html_path,
                     "risk_register_path": rr_path, "outputs": outputs, "ts": _now_iso()})
            return True, outputs

        except Exception as exc:
            emit_fn({"event": "stage_error", "stage": "assembly",
                     "step": step, "total": total, "error": str(exc), "ts": _now_iso()})
            return False, []
