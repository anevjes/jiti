"""
api_registry.py
---------------
Manages the central ``apis.json`` file that the JITi MCP server consumes.

When a new API is onboarded through the katalog pipeline, Azure OpenAI
generates a JSON entry from the swagger + docs.  This module handles:

  • Loading the existing registry (or creating an empty one).
  • Merging / upserting a new API entry (keyed on ``api_name``).
  • Writing the registry back to disk.
"""

import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

# Default location: katalog/apis.json
_DEFAULT_REGISTRY = Path(__file__).resolve().parent.parent / "apis.json"


# ---------------------------------------------------------------------------
# Read / write helpers
# ---------------------------------------------------------------------------

def load_registry(path: Path = _DEFAULT_REGISTRY) -> list[dict]:
    """Load the existing API registry, returning an empty list if missing."""
    if not path.exists():
        log.info("No existing apis.json found at %s — starting fresh.", path)
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            log.warning("apis.json root is not an array — resetting.")
            return []
        log.info("Loaded %d API(s) from %s", len(data), path)
        return data
    except json.JSONDecodeError:
        log.warning("apis.json is invalid JSON — resetting.")
        return []


def save_registry(registry: list[dict], path: Path = _DEFAULT_REGISTRY) -> Path:
    """Write the registry list back to disk as pretty-printed JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log.info("Saved %d API(s) to %s", len(registry), path)
    return path


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

def upsert_api(registry: list[dict], entry: dict) -> list[dict]:
    """
    Insert or update an API entry in the registry.

    Matching is done on ``api_name`` (case-insensitive).  If found, the
    existing entry is replaced; otherwise the new entry is appended.
    """
    name = entry.get("api_name", "").lower()
    for i, existing in enumerate(registry):
        if existing.get("api_name", "").lower() == name:
            log.info("Updating existing entry for '%s'.", entry["api_name"])
            registry[i] = entry
            return registry

    log.info("Appending new entry for '%s'.", entry.get("api_name"))
    registry.append(entry)
    return registry


# ---------------------------------------------------------------------------
# Parse LLM output → dict
# ---------------------------------------------------------------------------

def parse_api_json(raw: str) -> dict:
    """
    Extract a single API JSON object from the LLM response.

    The model might wrap the JSON in markdown fences or return an array.
    This function handles those cases gracefully.
    """
    text = raw.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else 3
        text = text[first_newline + 1:]
    if text.endswith("```"):
        text = text[: -3]
    text = text.strip()

    data = json.loads(text)

    # If the model returned an array, take the first element
    if isinstance(data, list):
        if len(data) == 0:
            raise ValueError("LLM returned an empty JSON array.")
        data = data[0]

    if not isinstance(data, dict):
        raise TypeError(f"Expected a JSON object, got {type(data).__name__}")

    return data
