# Katalog

**Katalog** is an automated API documentation pipeline that walks your API definitions, converts supporting docs to Markdown, and uses Azure OpenAI to generate structured **Data Model** and **SDK Proxy API Contract** specifications.

## Folder Structure

```
katalog/
├── apis/                         # One sub-folder per API
│   └── api1/
│       ├── contracts/            # Swagger / OpenAPI files (JSON, YAML)
│       ├── docs/                 # Source docs (DOCX, PDF, Markdown)
│       │   └── md/              # Auto-generated Markdown conversions
│       └── output/               # Generated specifications
│           ├── data_model.md
│           └── api_contract.md
├── skills/                       # (reserved for future use)
└── src/                          # Pipeline source code
    ├── generate_katalog.py       # Main entry-point
    ├── doc_converter.py          # DOCX/PDF → Markdown conversion
    ├── aoai_client.py            # Azure OpenAI client (DefaultAzureCredential)
    ├── prompts.py                # System/user prompt templates
    └── requirements.txt          # Python dependencies
```

## Prerequisites

- Python 3.10+
- An Azure OpenAI resource with a deployed model (e.g. `gpt-4o`)
- Your identity must have the **Cognitive Services OpenAI User** role on the Azure OpenAI resource
- Azure CLI logged in (`az login`) or another credential source supported by `DefaultAzureCredential`

## Setup

```bash
# From the repo root
pip install -r katalog/src/requirements.txt
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes | — | Azure OpenAI resource endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | No | `gpt-4o` | Deployment/model name |
| `AZURE_OPENAI_API_VERSION` | No | `2024-02-15-preview` | API version |

You can set these in a `.env` file at the repo root — the pipeline loads it automatically via `python-dotenv`.

## Usage

```bash
cd katalog/src

# Process all APIs under katalog/apis/
python generate_katalog.py

# Process a single API
python generate_katalog.py --api api1

# Dry-run — writes prompt previews to output/ without calling Azure OpenAI
python generate_katalog.py --dry-run

# Skip DOCX/PDF conversion (use when docs/md/ is already populated)
python generate_katalog.py --skip-convert

# Verbose logging
python generate_katalog.py -v
```

## Adding a New API

1. Create a folder under `katalog/apis/` (e.g. `apis/my-new-api/`)
2. Add the Swagger/OpenAPI file to `apis/my-new-api/contracts/`
3. Optionally add supporting docs (`.docx`, `.pdf`, `.md`) to `apis/my-new-api/docs/`
4. Run the pipeline — outputs land in `apis/my-new-api/output/`

## Pipeline Steps

1. **Convert docs** — DOCX and PDF files in `docs/` are converted to Markdown and written to `docs/md/`. Existing `.md` files are copied as-is.
2. **Gather inputs** — reads the Swagger/OpenAPI contract from `contracts/` and all Markdown from `docs/md/`.
3. **Generate Data Model** — calls Azure OpenAI with a structured prompt to produce `output/data_model.md`.
4. **Generate SDK Proxy API Contract** — calls Azure OpenAI to produce `output/api_contract.md`.

## Output Formats

### Data Model (`data_model.md`)

Entities with field tables, validation rules, state transitions, configuration file examples, and entity relationship diagrams.

### SDK Proxy API Contract (`api_contract.md`)

Endpoint specifications including path parameters, request/response forwarding rules, error tables, and example HTTP request/response pairs.
