"""
prompts.py
----------
System and user prompt templates for the two generation tasks:

1. **Data Model** – entity definitions, validation rules, relationships.
2. **SDK Proxy API Contract** – endpoint specs, error tables, examples.

Each public function returns ``(system_prompt, user_prompt)`` ready for
``aoai_client.generate()``.
"""

from datetime import date

# ═══════════════════════════════════════════════════════════════════════════
# 1. Data‑Model generation
# ═══════════════════════════════════════════════════════════════════════════

_DATA_MODEL_SYSTEM = """\
You are a senior API architect.
Your task is to produce a **Data Model** specification document in Markdown
for a given API, based on its Swagger/OpenAPI contract and any supplementary
documentation provided.

Follow this exact output structure (do NOT add extra top-level sections):

# Data Model: <API-friendly-name>

**Feature**: <feature-id>
**Date**: <today>

## Entities

For each meaningful entity (request, response, config, runtime object):

### <EntityName>

One-paragraph description.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ...   | ...  | ...      | ...         |

**Validation rules** (if applicable):
- bullet list

---

(repeat for every entity)

## Configuration Files

Show realistic YAML / env-file examples that match the entities above.

## Relationships

```
EntityA  ──1:1──▶  EntityB   (short explanation)
...
```

RULES:
- Use ONLY information from the swagger and docs supplied by the user.
- Where the swagger is sparse, infer reasonable fields and mark them with
  "(inferred)" in the description.
- Always include `Validation rules` and `State transitions` when they make sense.
- Output **only** the Markdown document — no preamble, no trailing commentary.
"""

def data_model_prompts(
    api_name: str,
    swagger_text: str,
    docs_markdown: str,
) -> tuple[str, str]:
    """Return (system, user) prompts for Data Model generation."""
    today = date.today().isoformat()
    user = (
        f"Generate the Data Model document for **{api_name}** (date: {today}).\n\n"
        f"## Swagger / OpenAPI contract\n\n```\n{swagger_text}\n```\n\n"
        f"## Supplementary documentation\n\n{docs_markdown}\n"
    )
    return _DATA_MODEL_SYSTEM, user


# ═══════════════════════════════════════════════════════════════════════════
# 2. SDK Proxy API Contract generation
# ═══════════════════════════════════════════════════════════════════════════

_API_CONTRACT_SYSTEM = """\
You are a senior API architect.
Your task is to produce an **SDK Proxy API Contract** specification document
in Markdown for a given API, based on its Swagger/OpenAPI contract and any
supplementary documentation provided.

Follow this exact output structure (do NOT add extra top-level sections):

# SDK Proxy API Contract

**Feature**: <feature-id>
**Date**: <today>
**Component**: <component-path>

## Base URL

Show local and debug URLs.

---

## Endpoints

For each endpoint the SDK should expose:

### <Endpoint title>

```
METHOD /path/{param}
```

Description, path params table, request/response forwarding rules,
success & error response tables, and full curl / HTTP examples.

---

(repeat for every endpoint)

## Orchestrator API Contract

If there is a backend orchestrator, include its endpoints here with
the same level of detail.

## Mock Destination API Contract

If there are mock/demo services, describe them here.

RULES:
- Use ONLY information from the swagger and docs supplied by the user.
- Where the swagger is sparse, infer reasonable endpoints and mark them
  with "(inferred)" in the description.
- Include realistic example request/response pairs.
- Output **only** the Markdown document — no preamble, no trailing commentary.
"""

def api_contract_prompts(
    api_name: str,
    swagger_text: str,
    docs_markdown: str,
) -> tuple[str, str]:
    """Return (system, user) prompts for SDK Proxy API Contract generation."""
    today = date.today().isoformat()
    user = (
        f"Generate the SDK Proxy API Contract for **{api_name}** (date: {today}).\n\n"
        f"## Swagger / OpenAPI contract\n\n```\n{swagger_text}\n```\n\n"
        f"## Supplementary documentation\n\n{docs_markdown}\n"
    )
    return _API_CONTRACT_SYSTEM, user
