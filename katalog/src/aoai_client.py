"""
aoai_client.py
--------------
Thin wrapper around Azure OpenAI using DefaultAzureCredential.
Provides a single ``generate()`` helper used by the katalog pipeline.
"""

import logging
import os
from pathlib import Path

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load .env from the same directory as this file
load_dotenv(Path(__file__).resolve().parent / ".env")

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration (reads from environment)
# ---------------------------------------------------------------------------
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# ---------------------------------------------------------------------------
# Client initialisation (DefaultAzureCredential – no API key needed)
# ---------------------------------------------------------------------------
_credential = DefaultAzureCredential()
_token_provider = get_bearer_token_provider(
    _credential, "https://cognitiveservices.azure.com/.default"
)


def _get_client() -> AzureOpenAI:
    if not AZURE_OPENAI_ENDPOINT:
        raise RuntimeError(
            "AZURE_OPENAI_ENDPOINT environment variable is not set. "
            "Set it to your Azure OpenAI resource endpoint."
        )
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_ad_token_provider=_token_provider,
        api_version=AZURE_OPENAI_API_VERSION,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """
    Send a chat completion request and return the assistant's response text.
    """
    client = _get_client()

    log.info("Calling Azure OpenAI (deployment=%s) …", AZURE_OPENAI_DEPLOYMENT)
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        # temperature=temperature,
    )

    content = response.choices[0].message.content
    log.info("Received response (%d chars).", len(content))
    return content
