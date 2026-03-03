"""
doc_converter.py
----------------
Walks katalog/apis/{api}/docs and converts any DOCX or PDF files to
Markdown, writing the output to katalog/apis/{api}/docs/md/.
Plain .md files are copied as-is into the md/ folder.
"""

import logging
import os
import shutil
from pathlib import Path

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Conversion helpers
# ---------------------------------------------------------------------------

def _convert_docx_to_md(src: Path) -> str:
    """Convert a .docx file to Markdown text using mammoth."""
    try:
        import mammoth
    except ImportError:
        raise ImportError(
            "mammoth is required for DOCX conversion. "
            "Install it with: pip install mammoth"
        )

    with open(src, "rb") as f:
        result = mammoth.convert_to_markdown(f)
        if result.messages:
            for msg in result.messages:
                log.warning("mammoth: %s", msg)
        return result.value


def _convert_pdf_to_md(src: Path) -> str:
    """Convert a PDF file to Markdown text using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "pdfplumber is required for PDF conversion. "
            "Install it with: pip install pdfplumber"
        )

    pages: list[str] = []
    with pdfplumber.open(src) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                pages.append(f"<!-- Page {i} -->\n{text}")
            else:
                pages.append(f"<!-- Page {i} (no extractable text) -->")
    return "\n\n---\n\n".join(pages)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".md"}


def convert_docs_for_api(api_dir: Path) -> list[Path]:
    """
    Given an API directory (e.g. katalog/apis/api1), find all docs in
    api_dir/docs, convert DOCX/PDF to markdown, copy existing .md files,
    and write everything into api_dir/docs/md/.

    Returns a list of paths to the generated markdown files.
    """
    docs_dir = api_dir / "docs"
    md_out_dir = docs_dir / "md"
    md_out_dir.mkdir(parents=True, exist_ok=True)

    if not docs_dir.exists():
        log.info("No docs/ folder in %s — skipping.", api_dir.name)
        return []

    generated: list[Path] = []

    for entry in sorted(docs_dir.iterdir()):
        # Skip the md output folder itself and any sub-directories
        if entry.is_dir():
            continue

        ext = entry.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            log.debug("Skipping unsupported file: %s", entry.name)
            continue

        out_name = entry.stem + ".md"
        out_path = md_out_dir / out_name

        try:
            if ext == ".docx":
                log.info("Converting DOCX → MD: %s", entry.name)
                md_text = _convert_docx_to_md(entry)
                out_path.write_text(md_text, encoding="utf-8")

            elif ext == ".pdf":
                log.info("Converting PDF  → MD: %s", entry.name)
                md_text = _convert_pdf_to_md(entry)
                out_path.write_text(md_text, encoding="utf-8")

            elif ext == ".md":
                log.info("Copying    MD  → MD: %s", entry.name)
                shutil.copy2(entry, out_path)

            generated.append(out_path)
            log.info("  ✓ %s", out_path)

        except Exception:
            log.exception("Failed to convert %s", entry.name)

    return generated


def walk_and_convert(apis_root: Path) -> dict[str, list[Path]]:
    """
    Walk all API directories under *apis_root* and convert docs.

    Returns a dict mapping API folder name → list of generated MD paths.
    """
    results: dict[str, list[Path]] = {}

    if not apis_root.exists():
        log.error("APIs root does not exist: %s", apis_root)
        return results

    for api_dir in sorted(apis_root.iterdir()):
        if not api_dir.is_dir():
            continue
        log.info("Processing API: %s", api_dir.name)
        generated = convert_docs_for_api(api_dir)
        results[api_dir.name] = generated
        log.info("  Generated %d markdown file(s) for %s", len(generated), api_dir.name)

    return results
