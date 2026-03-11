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
import logging

log = logging.getLogger(__name__)

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
- Do not truncate the yaml/json input.
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
    log.info("Prepared API Contract prompts for %s.", api_name)
    log.info(user)
    return _API_CONTRACT_SYSTEM, user


# ═══════════════════════════════════════════════════════════════════════════
# 3. API Registry (apis.json) generation
# ═══════════════════════════════════════════════════════════════════════════

_API_REGISTRY_SYSTEM = """\
You are a senior API architect.
Your task is to produce a **single JSON object** that describes an API for
a machine-readable registry.  This registry is consumed by an AI agent that
generates orchestration code, so include as much operational detail as
possible.

The output MUST be a valid JSON object (NOT an array) with this exact
top-level structure:

{
  "api_name": "<PascalCaseName>",
  "description": "<one-sentence description>",
  "base_url": "<base URL from the swagger, e.g. https://api.example.com/v1>",
  "auth_method": "<None | ApiKey | Bearer | OAuth2 | BasicAuth>",
  "auth_details": {
    "header_name": "<header name if ApiKey/Bearer, omit if None>",
    "token_env_var": "<suggested env-var name for the secret, omit if None>"
  },
  "rate_limit": "<e.g. '60 req/min' or 'unknown'>",
  "docs_url": "<link to official docs if known, or null>",
  "endpoints": [
    {
      "operation_id": "<operationId from swagger, or a descriptive slug>",
      "path": "/resource/{id}",
      "method": "GET",
      "summary": "<short one-line summary>",
      "description": "<detailed description of what this endpoint does, including edge cases>",
      "tags": ["<tag1>", "<tag2>"],
      "parameters": [
        {
          "name": "id",
          "in": "<path | query | header | body>",
          "type": "integer",
          "format": "<int32 | int64 | float | double | date | date-time | etc., or null>",
          "required": true,
          "description": "...",
          "default": null,
          "enum": null,
          "example": 1
        }
      ],
      "request_body": {
        "content_type": "application/json",
        "schema_summary": "<brief description of the request body structure>",
        "example": { "field": "value" }
      },
      "responses": {
        "200": {
          "description": "Successful response",
          "content_type": "application/json",
          "schema_summary": "<brief description of the response structure>",
          "example": { "id": 1, "name": "example" }
        },
        "400": {
          "description": "Bad request — missing or invalid parameters",
          "example": { "error": "Invalid input", "detail": "..." }
        },
        "404": {
          "description": "Resource not found",
          "example": { "error": "Not found" }
        }
      },
      "example_curl": "curl -X GET 'https://api.example.com/v1/resource/1' -H 'Authorization: Bearer $TOKEN'"
    }
  ]
}

RULES:
- Use ONLY information from the swagger and docs supplied by the user.
- Where the swagger is sparse, infer reasonable values and add
  "(inferred)" to the description.
- ``auth_method`` must be one of: None, ApiKey, Bearer, OAuth2, BasicAuth.
- If auth_method is "None", omit auth_details entirely.
- ``rate_limit`` should be "unknown" if not documented.
- Every endpoint in the swagger MUST appear in the ``endpoints`` array.
- For each parameter include ``in`` (path/query/header/body), ``format``,
  ``enum`` (if applicable), and a realistic ``example`` value.
- ``request_body`` is required for POST/PUT/PATCH endpoints; omit it for
  GET/DELETE unless the swagger explicitly defines one.
- ``responses`` must include at least the success case (2xx) and any error
  cases documented in the swagger.  Include a realistic ``example`` for
  each response code.
- ``example_curl`` must be a valid curl command that a developer could run
  to call the endpoint (use placeholder values like $TOKEN for secrets).
- ``schema_summary`` should be a concise human-readable description of the
  JSON structure, not a full JSON Schema.
- Output **only** the raw JSON object — no markdown fences, no commentary.
"""


def api_registry_prompts(
    api_name: str,
    swagger_text: str,
    docs_markdown: str,
) -> tuple[str, str]:
    """Return (system, user) prompts for API registry JSON generation."""
    today = date.today().isoformat()
    user = (
        f"Generate the API registry JSON entry for **{api_name}** (date: {today}).\n\n"
        f"## Swagger / OpenAPI contract\n\n```\n{swagger_text}\n```\n\n"
        f"## Supplementary documentation\n\n{docs_markdown}\n"
    )
    return _API_REGISTRY_SYSTEM, user
