"""
ai_search_client.py
-------------------
Manages Azure AI Search index creation and document ingestion for the
Katalog API registry.

Each API entry from ``apis.json`` is uploaded as a document with an
additional ``doc_contents`` field that contains all concatenated markdown
documentation from the API's ``docs/md/`` folder.

Environment variables
~~~~~~~~~~~~~~~~~~~~~
    AZURE_SEARCH_ENDPOINT   – e.g. https://<name>.search.windows.net
    AZURE_SEARCH_INDEX_NAME – index to create / upsert into (default: katalog-apis)

Authentication uses ``DefaultAzureCredential`` (same as the AOAI client).
"""

import json
import hashlib
import logging
import os
import re
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SearchableField,
    SimpleField,
)
from dotenv import load_dotenv

# Load .env from the same directory as this file
load_dotenv(Path(__file__).resolve().parent / ".env")

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "katalog-apis")

KATALOG_ROOT = Path(__file__).resolve().parent.parent  # katalog/
APIS_ROOT = KATALOG_ROOT / "apis"                      # katalog/apis/

_credential = DefaultAzureCredential()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_key(api_name: str) -> str:
    """
    Produce a safe document key from the api_name.

    Azure AI Search keys must match ``[a-zA-Z0-9_-]`` and be ≤ 1024 chars.
    We slugify the name and, if empty, fall back to a hash.
    """
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", api_name).strip("_")
    return slug if slug else hashlib.sha256(api_name.encode()).hexdigest()[:64]


def _read_md_docs_for_api(api_name: str) -> str:
    """Read and concatenate all markdown files from katalog/apis/<api>/docs/md/."""
    md_dir = APIS_ROOT / api_name / "docs" / "md"
    if not md_dir.exists():
        return ""

    parts: list[str] = []
    for md_file in sorted(md_dir.glob("*.md")):
        parts.append(f"## {md_file.stem}\n\n{md_file.read_text(encoding='utf-8', errors='replace')}")
    return "\n\n---\n\n".join(parts)


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------

def _build_index_definition() -> SearchIndex:
    """Return the SearchIndex definition for the katalog-apis index."""
    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
        ),
        SearchableField(
            name="api_name",
            type=SearchFieldDataType.String,
            filterable=True,
            sortable=True,
        ),
        SearchableField(
            name="description",
            type=SearchFieldDataType.String,
        ),
        SimpleField(
            name="base_url",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="auth_method",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SearchableField(
            name="auth_details",
            type=SearchFieldDataType.String,
        ),
        SimpleField(
            name="rate_limit",
            type=SearchFieldDataType.String,
            filterable=True,
        ),
        SimpleField(
            name="docs_url",
            type=SearchFieldDataType.String,
        ),
        SearchableField(
            name="endpoints_json",
            type=SearchFieldDataType.String,
        ),
        SearchableField(
            name="doc_contents",
            type=SearchFieldDataType.String,
        ),
    ]

    return SearchIndex(name=AZURE_SEARCH_INDEX_NAME, fields=fields)


def ensure_index() -> None:
    """Create or update the Azure AI Search index."""
    if not AZURE_SEARCH_ENDPOINT:
        raise RuntimeError(
            "AZURE_SEARCH_ENDPOINT environment variable is not set. "
            "Set it to your Azure AI Search endpoint (e.g. https://<name>.search.windows.net)."
        )

    index_client = SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=_credential,
    )

    index_def = _build_index_definition()
    index_client.create_or_update_index(index_def)
    log.info("Index '%s' created / updated on %s.", AZURE_SEARCH_INDEX_NAME, AZURE_SEARCH_ENDPOINT)


# ---------------------------------------------------------------------------
# Document ingestion
# ---------------------------------------------------------------------------

def _api_entry_to_document(entry: dict) -> dict:
    """
    Convert a single API registry entry (from apis.json) into a flat
    document suitable for Azure AI Search.
    """
    api_name = entry.get("api_name", "unknown")
    doc_contents = _read_md_docs_for_api(api_name)

    # Try a case-insensitive folder lookup if exact name doesn't match
    if not doc_contents:
        for d in APIS_ROOT.iterdir():
            if d.is_dir() and d.name.lower() == api_name.lower():
                doc_contents = _read_md_docs_for_api(d.name)
                break

    return {
        "id": _make_key(api_name),
        "api_name": api_name,
        "description": entry.get("description", ""),
        "base_url": entry.get("base_url", ""),
        "auth_method": entry.get("auth_method", ""),
        "auth_details": json.dumps(entry.get("auth_details", {}), ensure_ascii=False),
        "rate_limit": entry.get("rate_limit", ""),
        "docs_url": entry.get("docs_url", ""),
        "endpoints_json": json.dumps(entry.get("endpoints", []), ensure_ascii=False),
        "doc_contents": doc_contents,
    }


def ingest_registry(registry: list[dict]) -> int:
    """
    Upload every API entry in *registry* to Azure AI Search.

    Returns the number of documents successfully uploaded.
    """
    if not AZURE_SEARCH_ENDPOINT:
        raise RuntimeError(
            "AZURE_SEARCH_ENDPOINT environment variable is not set. "
            "Set it to your Azure AI Search endpoint."
        )

    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=_credential,
    )

    documents = [_api_entry_to_document(entry) for entry in registry]
    if not documents:
        log.warning("No documents to upload — registry is empty.")
        return 0

    result = search_client.upload_documents(documents=documents)
    succeeded = sum(1 for r in result if r.succeeded)
    failed = sum(1 for r in result if not r.succeeded)

    if failed:
        for r in result:
            if not r.succeeded:
                log.error("  Failed to upload doc '%s': %s", r.key, r.error_message)

    log.info(
        "Uploaded %d document(s) to index '%s' (%d succeeded, %d failed).",
        len(documents), AZURE_SEARCH_INDEX_NAME, succeeded, failed,
    )
    return succeeded
