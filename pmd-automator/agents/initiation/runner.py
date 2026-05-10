"""
Initiation Agent workflow runner.
Stages: Ingestion → Validation → Extraction → Assembly
Emits newline-delimited JSON events to stdout for Streamlit to consume.
All sub-module print() output is redirected to stderr.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Capture real stdout before any possible redirection
_STDOUT = sys.stdout

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "common" / "validation" / "sow_headers.json"
TEMPLATE_PATH = REPO_ROOT / "common" / "templates" / "charter_master.md"

STAGES = [
    ("ingestion",     "Ingestion"),
    ("validation",    "Validation"),
    ("extraction",    "Extraction"),
    ("assembly",      "Assembly"),
]


# ---------------------------------------------------------------------------
# Event helpers
# ---------------------------------------------------------------------------

def emit(event: dict) -> None:
    print(json.dumps(event), file=_STDOUT, flush=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextlib.contextmanager
def _muted():
    """Redirect sys.stdout to stderr to suppress sub-module prints."""
    old = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old


# ---------------------------------------------------------------------------
# Stage 1 — Ingestion
# ---------------------------------------------------------------------------

def run_ingestion(project_root: Path, state_path: Path) -> bool:
    step, total = 1, len(STAGES)
    emit({"event": "stage_start", "stage": "ingestion", "label": "Ingestion",
          "step": step, "total": total})
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from agents.initiation.skills.ingestion.parser import scan_inbox  # type: ignore

        inbox = project_root / "00_inbox"
        if not inbox.exists():
            inbox.mkdir(parents=True)

        with _muted():
            n = scan_inbox(inbox, project_root, state_path)

        emit({"event": "stage_done", "stage": "ingestion", "step": step, "total": total,
              "docs_ingested": n})
        return True

    except Exception as exc:
        emit({"event": "stage_error", "stage": "ingestion",
              "step": step, "total": total, "error": str(exc)})
        return False


# ---------------------------------------------------------------------------
# Stage 2 — Validation
# ---------------------------------------------------------------------------

def run_validation(project_root: Path) -> bool:
    step, total = 2, len(STAGES)
    emit({"event": "stage_start", "stage": "validation", "label": "Validation",
          "step": step, "total": total})
    try:
        from agents.initiation.skills.validation.validator import validate_project  # type: ignore

        result = validate_project(project_root, SCHEMA_PATH)

        if not result["passed"]:
            # Collect all unique missing anchors across all documents
            all_missing: list[str] = []
            if result.get("error"):
                all_missing = [result["error"]]
            else:
                seen: set[str] = set()
                for missing_list in result["results"].values():
                    for m in missing_list:
                        if m not in seen:
                            seen.add(m)
                            all_missing.append(m)

            emit({"event": "validation_error", "missing": all_missing,
                  "details": result.get("results", {})})
            emit({"event": "stage_error", "stage": "validation",
                  "step": step, "total": total, "error": "Validation failed"})
            return False

        emit({"event": "stage_done", "stage": "validation", "step": step, "total": total})
        return True

    except Exception as exc:
        emit({"event": "stage_error", "stage": "validation",
              "step": step, "total": total, "error": str(exc)})
        return False


# ---------------------------------------------------------------------------
# Stage 3 — Extraction
# ---------------------------------------------------------------------------

def _strip_frontmatter(content: str) -> str:
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip()
    return content


def _extract_section(content: str, anchor_id: str, patterns: list[str]) -> str:
    """Extract a named section by anchor tag or heading fallback."""
    lc = content.lower()
    open_tag = f"<!-- anchor:{anchor_id} -->"
    close_tag = f"<!-- anchor:{anchor_id}:end -->"

    if open_tag in lc:
        start = lc.index(open_tag) + len(open_tag)
        if close_tag in lc[start:]:
            end = lc.index(close_tag, start)
            return content[start:end].strip()
        rest = content[start:]
        m = re.search(r"\n#{1,3} ", rest)
        return rest[: m.start()].strip() if m else rest.strip()

    for pattern in patterns:
        m = re.search(
            rf"(?m)^(#{1,4})\s+{re.escape(pattern)}\s*$",
            content, re.IGNORECASE,
        )
        if m:
            level = len(m.group(1))
            after = content[m.end():]
            nxt = re.search(rf"(?m)^#{{1,{level}}} ", after)
            body = after[: nxt.start()] if nxt else after
            return (content[m.start(): m.end()] + body).strip()

    return ""


def run_extraction(project_root: Path) -> bool:
    step, total = 3, len(STAGES)
    emit({"event": "stage_start", "stage": "extraction", "label": "Extraction",
          "step": step, "total": total})
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        working_docs = sorted((project_root / "02_working_docs").glob("*.md"))
        snippets_dir = project_root / "03_ai_snippets"
        snippets_dir.mkdir(parents=True, exist_ok=True)

        anchors = list(schema["fallback_patterns"].items())
        total_ops = max(len(working_docs) * len(anchors), 1)
        done = 0

        for doc in working_docs:
            raw = doc.read_text(encoding="utf-8")
            body = _strip_frontmatter(raw)

            for anchor_id, patterns in anchors:
                extracted = _extract_section(body, anchor_id, patterns)
                if not extracted:
                    extracted = f"<!-- NO_{anchor_id.upper()}_FOUND -->\n\n> No {anchor_id} section detected in source document."

                front = (
                    f"---\n"
                    f"skill: extract-{anchor_id}\n"
                    f"source: {doc.name}\n"
                    f"extracted_at: {_now_iso()}\n"
                    f"anchor: {anchor_id}\n"
                    f"---\n\n"
                )
                out = snippets_dir / f"{doc.stem}_{anchor_id}.md"
                out.write_text(front + extracted, encoding="utf-8")

                done += 1
                sub_pct = done / total_ops
                emit({
                    "event": "stage_progress",
                    "stage": "extraction",
                    "step": step,
                    "total": total,
                    "sub_pct": sub_pct,
                    "label": f"Extracting '{anchor_id}' from {doc.name}",
                })

        emit({"event": "stage_done", "stage": "extraction", "step": step, "total": total})
        return True

    except Exception as exc:
        emit({"event": "stage_error", "stage": "extraction",
              "step": step, "total": total, "error": str(exc)})
        return False


# ---------------------------------------------------------------------------
# Stage 4 — Assembly
# ---------------------------------------------------------------------------

def run_assembly(project_root: Path) -> bool:
    step, total = 4, len(STAGES)
    emit({"event": "stage_start", "stage": "assembly", "label": "Assembly",
          "step": step, "total": total})
    try:
        snippets_dir = project_root / "03_ai_snippets"
        final_dir = project_root / "04_final_deliverables"
        final_dir.mkdir(parents=True, exist_ok=True)

        # Group snippets by source stem
        section_order = ["scope", "stakeholders", "deliverables", "risks"]
        sections: dict[str, dict[str, str]] = {}

        for snippet in sorted(snippets_dir.glob("*.md")):
            parts = snippet.stem.rsplit("_", 1)
            if len(parts) != 2:
                continue
            stem, anchor = parts
            content = snippet.read_text(encoding="utf-8")
            content = _strip_frontmatter(content)
            sections.setdefault(stem, {})[anchor] = content

        # Build one charter per source document
        output_paths: list[str] = []
        for stem, anchor_map in sections.items():
            lines = [
                f"# Project Charter — {stem.replace('_', ' ').title()}",
                f"\n_Generated: {_now_iso()}_\n",
                "---\n",
            ]
            for anchor in section_order:
                if anchor in anchor_map:
                    lines.append(f"## {anchor.title()}\n")
                    lines.append(anchor_map[anchor])
                    lines.append("\n---\n")

            # Append remaining anchors not in section_order
            for anchor, content in anchor_map.items():
                if anchor not in section_order:
                    lines.append(f"## {anchor.title()}\n")
                    lines.append(content)
                    lines.append("\n---\n")

            out_path = final_dir / f"{stem}_charter.md"
            out_path.write_text("\n".join(lines), encoding="utf-8")
            output_paths.append(str(out_path.relative_to(project_root)))

        emit({"event": "stage_done", "stage": "assembly", "step": step, "total": total,
              "outputs": output_paths})
        emit({"event": "complete", "outputs": output_paths})
        return True

    except Exception as exc:
        emit({"event": "stage_error", "stage": "assembly",
              "step": step, "total": total, "error": str(exc)})
        return False


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Initiation Agent workflow runner")
    ap.add_argument("--project-id", required=True)
    ap.add_argument(
        "--project-root",
        default=None,
        help="Absolute path to project folder (default: projects/<project-id>)",
    )
    ap.add_argument(
        "--state",
        default=None,
        help="Path to state JSON (default: state/<project-id>_state.json)",
    )
    args = ap.parse_args()

    project_root = (
        Path(args.project_root).resolve()
        if args.project_root
        else REPO_ROOT / "projects" / args.project_id
    )
    state_path = (
        Path(args.state).resolve()
        if args.state
        else REPO_ROOT / "state" / f"{args.project_id}_state.json"
    )

    stages = [
        lambda: run_ingestion(project_root, state_path),
        lambda: run_validation(project_root),
        lambda: run_extraction(project_root),
        lambda: run_assembly(project_root),
    ]

    for fn in stages:
        if not fn():
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
