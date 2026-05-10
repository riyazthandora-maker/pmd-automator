"""
Validation skill: checks working documents for required SOW sections.
Can be run standalone or imported by runner.py.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_SCHEMA = _REPO_ROOT / "common" / "validation" / "sow_headers.json"


def _strip_frontmatter(content: str) -> str:
    """Remove YAML front-matter block from Markdown content."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3 :].lstrip()
    return content


def validate_document(content: str, schema: dict) -> list[str]:
    """
    Return list of missing anchor IDs for a single document.
    Empty list → document passes validation.
    """
    body = _strip_frontmatter(content).lower()
    missing: list[str] = []

    for anchor_id, patterns in schema["fallback_patterns"].items():
        # Check explicit anchor comment tag
        if f"<!-- anchor:{anchor_id} -->" in body:
            continue

        # Fallback: search for a matching heading
        found = any(
            re.search(
                rf"(?m)^#{1,4}\s+{re.escape(p)}\s*$",
                body,
                re.IGNORECASE,
            )
            for p in patterns
        )
        if not found:
            missing.append(anchor_id)

    return missing


def validate_project(project_root: Path, schema_path: Path) -> dict:
    """
    Validate all .md files in 02_working_docs against the schema.

    Returns:
        {
          "passed": bool,
          "results": { "<filename>": ["<missing_anchor>", ...] },
          "error": "<str>"   # only present when passed=False due to setup issue
        }
    """
    if not schema_path.exists():
        return {"passed": False, "results": {}, "error": f"Schema not found: {schema_path}"}

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    working_dir = project_root / "02_working_docs"

    if not working_dir.exists():
        return {"passed": False, "results": {}, "error": "Directory 02_working_docs does not exist"}

    docs = sorted(working_dir.glob("*.md"))
    if not docs:
        return {"passed": False, "results": {}, "error": "No documents found in 02_working_docs"}

    results: dict[str, list[str]] = {}
    for doc in docs:
        content = doc.read_text(encoding="utf-8")
        missing = validate_document(content, schema)
        if missing:
            results[doc.name] = missing

    return {"passed": not bool(results), "results": results}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="PMO SOW validation skill")
    ap.add_argument("--project-root", required=True, help="Path to project folder")
    ap.add_argument("--schema", default=str(_DEFAULT_SCHEMA), help="Path to sow_headers.json")
    args = ap.parse_args()

    result = validate_project(Path(args.project_root), Path(args.schema))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
