#!/usr/bin/env python3
"""
generate_katalog.py  –  main entry-point
-----------------------------------------
Walk ``katalog/apis/``, convert docs → markdown, gather swagger contracts,
and call Azure OpenAI to produce:

  • ``<api>/output/data_model.md``      – Data Model specification
  • ``<api>/output/api_contract.md``    – SDK Proxy API Contract
  • ``katalog/apis.json``               – Central API registry (appended/upserted)

Usage
-----
    cd katalog/src
    python generate_katalog.py                     # process all APIs
    python generate_katalog.py --api api1          # process only api1
    python generate_katalog.py --skip-convert      # skip doc conversion step
    python generate_katalog.py --dry-run           # build prompts but don't call OpenAI
"""

import argparse
import logging
import sys
from pathlib import Path

# Local helpers
from doc_converter import walk_and_convert, convert_docs_for_api
from aoai_client import generate
from prompts import data_model_prompts, api_contract_prompts, api_registry_prompts
from api_registry import load_registry, save_registry, upsert_api, parse_api_json
from ai_search_client import ensure_index, ingest_registry

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
KATALOG_ROOT = Path(__file__).resolve().parent.parent        # katalog/
APIS_ROOT = KATALOG_ROOT / "apis"                            # katalog/apis/

log = logging.getLogger("katalog")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_swagger(api_dir: Path) -> str:
    """Read the first swagger / OpenAPI file found under api_dir/contracts/."""
    contracts_dir = api_dir / "contracts"
    if not contracts_dir.exists():
        return ""

    # Look for common swagger file names / extensions
    for pattern in ("*.json", "*.yaml", "*.yml", "swagger*", "openapi*", "*"):
        for f in sorted(contracts_dir.glob(pattern)):
            if f.is_file() and f.stat().st_size > 0:
                log.info("  Using swagger file: %s", f.name)
                return f.read_text(encoding="utf-8", errors="replace")

    # Fallback: try every file in contracts/
    for f in sorted(contracts_dir.iterdir()):
        if f.is_file() and f.stat().st_size > 0:
            return f.read_text(encoding="utf-8", errors="replace")

    log.warning("  No non-empty swagger file found in %s", contracts_dir)
    return ""


def _read_md_docs(api_dir: Path) -> str:
    """Concatenate all markdown files in api_dir/docs/md/ into one string."""
    md_dir = api_dir / "docs" / "md"
    if not md_dir.exists():
        return "(no supplementary docs available)"

    parts: list[str] = []
    for md_file in sorted(md_dir.glob("*.md")):
        parts.append(f"### {md_file.stem}\n\n{md_file.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(parts) if parts else "(no supplementary docs available)"


def _write_output(api_dir: Path, filename: str, content: str) -> Path:
    """Write *content* to api_dir/output/<filename> and return the path."""
    out_dir = api_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(content, encoding="utf-8")
    log.info("  ✓ Wrote %s", out_path)
    return out_path


# ---------------------------------------------------------------------------
# Per-API pipeline
# ---------------------------------------------------------------------------

def process_api(
    api_dir: Path,
    registry: list[dict],
    *,
    skip_convert: bool = False,
    dry_run: bool = False,
) -> None:
    """Run the full pipeline for one API directory."""
    api_name = api_dir.name
    log.info("=" * 60)
    log.info("Processing API: %s", api_name)
    log.info("=" * 60)

    # 1. Convert docs (docx/pdf → md)
    if not skip_convert:
        log.info("[1/6] Converting docs …")
        convert_docs_for_api(api_dir)
    else:
        log.info("[1/6] Skipping doc conversion (--skip-convert)")

    # 2. Gather inputs
    log.info("[2/6] Gathering swagger + docs …")
    swagger_text = _read_swagger(api_dir)
    docs_md = _read_md_docs(api_dir)

    if not swagger_text and docs_md == "(no supplementary docs available)":
        log.warning("  No swagger and no docs found for %s — skipping generation.", api_name)
        return

    # 3. Generate Data Model
    log.info("[3/6] Generating Data Model …")
    sys_dm, usr_dm = data_model_prompts(api_name, swagger_text, docs_md)
    if dry_run:
        log.info("  [dry-run] Would call Azure OpenAI for Data Model")
        _write_output(api_dir, "data_model_prompt_PREVIEW.md", f"# SYSTEM\n\n{sys_dm}\n\n# USER\n\n{usr_dm}")
    else:
        dm_result = generate(sys_dm, usr_dm)
        _write_output(api_dir, "data_model.md", dm_result)

    # 4. Generate SDK Proxy API Contract
    log.info("[4/6] Generating SDK Proxy API Contract …")
    sys_ac, usr_ac = api_contract_prompts(api_name, swagger_text, docs_md)

    if dry_run:
        log.info("  [dry-run] Would call Azure OpenAI for API Contract")
        _write_output(api_dir, "api_contract_prompt_PREVIEW.md", f"# SYSTEM\n\n{sys_ac}\n\n# USER\n\n{usr_ac}")
    else:
        ac_result = generate(sys_ac, usr_ac)
        _write_output(api_dir, "api_contract.md", ac_result)

    # 5. Generate / upsert API registry entry (apis.json)
    log.info("[5/6] Generating API registry entry …")
    sys_reg, usr_reg = api_registry_prompts(api_name, swagger_text, docs_md)
    if dry_run:
        log.info("  [dry-run] Would call Azure OpenAI for API registry entry")
        _write_output(api_dir, "api_registry_prompt_PREVIEW.md", f"# SYSTEM\n\n{sys_reg}\n\n# USER\n\n{usr_reg}")
    else:
        raw_json = generate(sys_reg, usr_reg, temperature=0.0)
        try:
            entry = parse_api_json(raw_json)
            upsert_api(registry, entry)
            # Also save the per-API copy for reference
            import json
            _write_output(api_dir, "api_registry_entry.json", json.dumps(entry, indent=2, ensure_ascii=False))
        except (ValueError, TypeError) as exc:
            log.error("  Failed to parse API registry JSON for %s: %s", api_name, exc)
            _write_output(api_dir, "api_registry_entry_RAW.txt", raw_json)

    # NOTE: Step 6 (AI Search ingest) runs after all APIs are processed.
    log.info("Done with %s.\n", api_name)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Data Model & API Contract docs for each API in katalog/apis/"
    )
    parser.add_argument(
        "--api",
        type=str,
        default=None,
        help="Process only this API folder name (e.g. api1). Default: all.",
    )
    parser.add_argument(
        "--skip-convert",
        action="store_true",
        help="Skip the DOCX/PDF → Markdown conversion step.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build prompts and write them to output/ but do NOT call Azure OpenAI.",
    )
    parser.add_argument(
        "--skip-search",
        action="store_true",
        help="Skip the Azure AI Search index creation and document ingestion step.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    args = parser.parse_args()

    # Logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )

    if not APIS_ROOT.exists():
        log.error("APIs root not found: %s", APIS_ROOT)
        sys.exit(1)

    # Determine which APIs to process
    if args.api:
        target = APIS_ROOT / args.api
        if not target.is_dir():
            log.error("API directory not found: %s", target)
            sys.exit(1)
        api_dirs = [target]
    else:
        api_dirs = sorted(d for d in APIS_ROOT.iterdir() if d.is_dir())

    if not api_dirs:
        log.warning("No API directories found under %s", APIS_ROOT)
        sys.exit(0)

    log.info("Found %d API(s) to process: %s", len(api_dirs), [d.name for d in api_dirs])

    # Load the central API registry
    registry_path = KATALOG_ROOT / "apis.json"
    registry = load_registry(registry_path)

    for api_dir in api_dirs:
        process_api(api_dir, registry, skip_convert=args.skip_convert, dry_run=args.dry_run)

    # Persist the (possibly updated) registry
    if not args.dry_run:
        save_registry(registry, registry_path)
        log.info("Registry saved to %s (%d API(s)).", registry_path, len(registry))
    else:
        log.info("[dry-run] Would save registry with %d API(s) to %s", len(registry), registry_path)

    # 6. Ingest into Azure AI Search
    if not args.skip_search and not args.dry_run:
        log.info("[6/6] Ingesting %d API(s) into Azure AI Search …", len(registry))
        try:
            ensure_index()
            ingested = ingest_registry(registry)
            log.info("AI Search: %d document(s) ingested successfully.", ingested)
        except Exception as exc:
            log.error("AI Search ingestion failed: %s", exc)
            log.error("Set AZURE_SEARCH_ENDPOINT in .env and ensure access is configured.")
    elif args.dry_run:
        log.info("[dry-run] Would ingest %d API(s) into Azure AI Search.", len(registry))
    else:
        log.info("[6/6] Skipping Azure AI Search ingestion (--skip-search).")

    log.info("All done.")


if __name__ == "__main__":
    main()
