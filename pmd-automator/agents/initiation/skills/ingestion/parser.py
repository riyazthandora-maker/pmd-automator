"""
Ingestion skill: monitors 00_inbox for PDFs, converts to Markdown,
archives originals to 01_raw_archive, writes to 02_working_docs,
and updates project_alpha_state.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# PDF → Markdown conversion backends
# ---------------------------------------------------------------------------

def _convert_pymupdf4llm(pdf_path: Path) -> str:
    import pymupdf4llm  # type: ignore
    return pymupdf4llm.to_markdown(str(pdf_path))


def _convert_marker(pdf_path: Path) -> str:
    from marker.convert import convert_single_pdf  # type: ignore
    from marker.models import load_all_models  # type: ignore
    models = load_all_models()
    full_text, _, _ = convert_single_pdf(str(pdf_path), models)
    return full_text


def _convert_pymupdf(pdf_path: Path) -> str:
    import fitz  # type: ignore  (PyMuPDF)
    doc = fitz.open(str(pdf_path))
    pages: list[str] = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        pages.append(f"## Page {i}\n\n{text}")
    doc.close()
    return "\n\n---\n\n".join(pages)


_BACKENDS: list[tuple[str, object]] = [
    ("pymupdf4llm", _convert_pymupdf4llm),
    ("marker-pdf",  _convert_marker),
    ("pymupdf",     _convert_pymupdf),
]


def pdf_to_markdown(pdf_path: Path) -> str:
    """Convert a PDF to Markdown using the first available backend."""
    errors: list[str] = []
    for name, fn in _BACKENDS:
        try:
            result = fn(pdf_path)  # type: ignore[operator]
            print(f"[ingestion] Converted '{pdf_path.name}' via {name}")
            return result
        except ImportError:
            errors.append(f"  {name}: not installed")
        except Exception as exc:
            errors.append(f"  {name}: {exc}")
    raise RuntimeError(
        f"All PDF backends failed for '{pdf_path.name}':\n" + "\n".join(errors)
    )


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state(state_path: Path) -> dict:
    if state_path.exists():
        with state_path.open(encoding="utf-8") as f:
            return json.load(f)
    return {
        "project_id": state_path.stem.replace("_state", ""),
        "status": "PENDING",
        "last_updated": _now_iso(),
        "documents": [],
    }


def save_state(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = _now_iso()
    with state_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _already_ingested(state: dict, file_hash: str) -> bool:
    return any(d.get("source_hash") == file_hash for d in state.get("documents", []))


# ---------------------------------------------------------------------------
# Core ingestion
# ---------------------------------------------------------------------------

def ingest_pdf(
    pdf_path: Path,
    project_root: Path,
    state_path: Path,
) -> Optional[dict]:
    """
    Ingest one PDF through the pipeline:
      hash-check → convert → archive original → write markdown → update state.

    Returns the new document entry dict, or None if already ingested.
    """
    state = load_state(state_path)
    file_hash = _sha256(pdf_path)

    if _already_ingested(state, file_hash):
        print(f"[ingestion] Skipping '{pdf_path.name}' — already ingested (hash match)")
        return None

    try:
        markdown = pdf_to_markdown(pdf_path)
    except RuntimeError as exc:
        print(f"[ingestion] ERROR: {exc}")
        return None

    # Archive the original PDF (immutable copy)
    archive_dir = project_root / "01_raw_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived_pdf = archive_dir / pdf_path.name
    shutil.copy2(str(pdf_path), str(archived_pdf))

    # Write Markdown with YAML front-matter to working docs
    working_dir = project_root / "02_working_docs"
    working_dir.mkdir(parents=True, exist_ok=True)
    working_md = working_dir / (pdf_path.stem + ".md")
    ingested_at = _now_iso()
    front_matter = (
        f"---\n"
        f"source: {pdf_path.name}\n"
        f"ingested_at: {ingested_at}\n"
        f"source_hash: {file_hash}\n"
        f"---\n\n"
    )
    working_md.write_text(front_matter + markdown, encoding="utf-8")

    # Persist state
    doc_entry = {
        "source_filename": pdf_path.name,
        "source_hash": file_hash,
        "ingested_at": ingested_at,
        "raw_archive_path": str(archived_pdf.relative_to(project_root)),
        "working_doc_path": str(working_md.relative_to(project_root)),
        "status": "INGESTED",
    }
    state["documents"].append(doc_entry)
    state["status"] = "INGESTED"
    save_state(state_path, state)

    print(
        f"[ingestion] '{pdf_path.name}' ingested\n"
        f"  archive → {doc_entry['raw_archive_path']}\n"
        f"  working → {doc_entry['working_doc_path']}\n"
        f"  state   → {state_path}"
    )
    return doc_entry


# ---------------------------------------------------------------------------
# Inbox scanning
# ---------------------------------------------------------------------------

def scan_inbox(inbox_dir: Path, project_root: Path, state_path: Path) -> int:
    """Process all PDFs currently in inbox_dir. Returns the count newly ingested."""
    if not inbox_dir.exists():
        raise FileNotFoundError(f"Inbox directory not found: {inbox_dir}")
    pdfs = sorted(inbox_dir.glob("*.pdf"))
    if not pdfs:
        print(f"[ingestion] No PDFs found in {inbox_dir}")
        return 0
    count = sum(1 for pdf in pdfs if ingest_pdf(pdf, project_root, state_path) is not None)
    return count


# ---------------------------------------------------------------------------
# Watch mode
# ---------------------------------------------------------------------------

def _watch_watchdog(inbox_dir: Path, project_root: Path, state_path: Path) -> None:
    from watchdog.observers import Observer  # type: ignore
    from watchdog.events import FileSystemEventHandler  # type: ignore

    class _Handler(FileSystemEventHandler):
        def on_created(self, event):  # type: ignore[override]
            p = Path(event.src_path)
            if not event.is_directory and p.suffix.lower() == ".pdf":
                # Brief pause so the file is fully written before we read it
                time.sleep(0.5)
                ingest_pdf(p, project_root, state_path)

    observer = Observer()
    observer.schedule(_Handler(), str(inbox_dir), recursive=False)
    observer.start()
    print(f"[ingestion] Watching {inbox_dir} (watchdog) — press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()


def _watch_polling(
    inbox_dir: Path,
    project_root: Path,
    state_path: Path,
    interval: int,
) -> None:
    print(f"[ingestion] Polling {inbox_dir} every {interval}s — press Ctrl+C to stop")
    seen: set[str] = set()
    try:
        while True:
            for pdf in sorted(inbox_dir.glob("*.pdf")):
                key = f"{pdf.name}:{pdf.stat().st_size}"
                if key not in seen:
                    seen.add(key)
                    ingest_pdf(pdf, project_root, state_path)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("[ingestion] Stopped.")


def watch(
    inbox_dir: Path,
    project_root: Path,
    state_path: Path,
    poll_interval: int = 10,
) -> None:
    """Start continuous monitoring of inbox_dir, draining any existing PDFs first."""
    scan_inbox(inbox_dir, project_root, state_path)
    try:
        _watch_watchdog(inbox_dir, project_root, state_path)
    except ImportError:
        print("[ingestion] watchdog not installed — falling back to polling")
        _watch_polling(inbox_dir, project_root, state_path, interval=poll_interval)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _default_project_root() -> Path:
    # Assumes this file lives at agents/initiation/skills/ingestion/parser.py
    repo_root = Path(__file__).resolve().parents[4]
    return repo_root / "projects" / "project_alpha"


def _default_state_path(project_root: Path) -> Path:
    return project_root.parents[1] / "state" / "project_alpha_state.json"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="PMO Initiation — ingestion skill",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument(
        "--project-root",
        default=str(_default_project_root()),
        help="Path to the project folder (contains 00_inbox, 01_raw_archive, …)",
    )
    ap.add_argument(
        "--state",
        default=None,
        help="Path to state JSON (default: <repo>/state/project_alpha_state.json)",
    )
    ap.add_argument(
        "--watch",
        action="store_true",
        help="Run continuously, processing PDFs as they arrive",
    )
    ap.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        metavar="SECONDS",
        help="Polling interval when watchdog is unavailable",
    )
    args = ap.parse_args()

    project_root = Path(args.project_root).resolve()
    inbox_dir = project_root / "00_inbox"
    state_path = Path(args.state).resolve() if args.state else _default_state_path(project_root)

    if args.watch:
        watch(inbox_dir, project_root, state_path, poll_interval=args.poll_interval)
    else:
        n = scan_inbox(inbox_dir, project_root, state_path)
        print(f"[ingestion] Done — {n} document(s) newly ingested.")
