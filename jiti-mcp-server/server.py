import json
import logging
import os
import uuid
import requests
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv

log = logging.getLogger(__name__)



# Load environment variables
load_dotenv()


# Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# Azure AD token-based auth for Azure OpenAI
credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

# content safety / dynamic sessions
ACA_POOL_MANAGEMENT_ENDPOINT = os.getenv("ACA_POOL_MANAGEMENT_ENDPOINT")

# Initialize FastMCP Server
mcp = FastMCP(
    name="JITi-Server",
    instructions="""You are an agent that analyzes the user's intent, matches it against available APIs, 
generates an orchestration script, and executes it in a secure sandbox.""",
    host="0.0.0.0",
    port=8001,
    streamable_http_path="/",
    stateless_http=True,
)

def load_api_definitions():
    """Loads the API definitions from the JSON file."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "apis.json")
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "[]"

def generate_orchestration_code(user_query: str, api_defs: str) -> str:
    """
    Uses Azure OpenAI to generate Python code based on the user query and API definitions.
    """
    if not AZURE_OPENAI_ENDPOINT:
        return "print('Error: Azure OpenAI endpoint not configured.')"

    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version=AZURE_OPENAI_API_VERSION
    )

    system_prompt = f"""
    You are an expert API Orchestrator. 
    Your goal is to analyze the user's intent and generate a Python script to satisfy their request using the available APIs.
    
    You have access to the following APIs defined in JSON format:
    {api_defs}

    RULES:
    1. Only use the `requests` library for HTTP calls.
    2. Only generate code for READ (GET) operations. Do not perform POST, PUT, DELETE.
    3. The code must print the final result to stdout in JSON format so it can be captured.
    4. Handle errors gracefully (e.g., check response status codes, catch exceptions, print meaningful error messages).
    5. Generate code that calls the REAL API endpoints defined in the JSON. Use the actual base_url and endpoint paths. 
       Do NOT mock, simulate, or hardcode any response data. The code must make real HTTP requests and return real data.
    6. Include any required authentication headers as defined in auth_details (e.g., Bearer token from environment variables).
    7. Use `os.getenv()` to read any required auth tokens or API keys from environment variables as specified in the API definitions.
    8. Return ONLY the valid Python code block. No markdown fencing (```python).
    """

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        # temperature=0.1
    )

    code = response.choices[0].message.content
    # Strip markdown if LLM adds it despite instructions
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    
    return code.strip()

def execute_in_dynamic_session(code: str) -> str:
    """
    Executes the generated Python code in an Azure Container App Dynamic Session.
    """
    if not ACA_POOL_MANAGEMENT_ENDPOINT:
        return "Error: ACA_POOL_MANAGEMENT_ENDPOINT not configured. Cannot execute code."

    # Build URL with required identifier query param (unique per execution)
    session_id = str(uuid.uuid4())
    base = ACA_POOL_MANAGEMENT_ENDPOINT.rstrip("/")
    url = f"{base}/code/execute?api-version=2024-02-02-preview&identifier={session_id}"

    log.info("Executing code in Azure Container App Dynamic Session...")
    log.info(f"Endpoint: {url}")
    log.info(f"Code to execute:\n{code}")
    token = credential.get_token("https://dynamicsessions.io/.default").token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "properties": {
            "codeInputType": "inline",
            "executionType": "synchronous",
            "code": code
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        log.info(f"Response status: {response.status_code}")
        log.info(f"Response body: {response.text}")
        response.raise_for_status()
        result = response.json()
        
        # The result structure usually contains 'properties' -> 'output' or 'stdout'
        # Adjust based on the exact API version response shape
        return result.get("properties", {}).get("stdout", "No output returned.")
        
    except Exception as e:
        return f"Execution Failed: {str(e)}"

@mcp.tool("generate-jiti")
def generate_jiti(query: str) -> str:
    """
    Analyzes the user's intent, matches it against available APIs, 
    generates an orchestration script, and executes it in a secure sandbox.
    
    Args:
        query: The user's natural language request (e.g., "What is the weather in Perth?")
    """
    # 1. Load context
    api_defs = load_api_definitions()
    
    # 2. Generate Code via Azure OpenAI
    try:
        generated_code = generate_orchestration_code(query, api_defs)
    except Exception as e:
        return f"Failed to generate code: {str(e)}"

    # 3. Serialize and Execute in Dynamic Session
    # Note: For this demo, if the user doesn't have a live Session Pool, 
    # we might want to return the code for inspection. 
    # However, the prompt asked to wrap it and pass it to the session.
    
    if os.getenv("ACA_POOL_MANAGEMENT_ENDPOINT"):
        execution_result = execute_in_dynamic_session(generated_code)
        return f"Intent Analyzed. \nGenerated Logic:\n{generated_code}\n\nExecution Result:\n{execution_result}"
    else:
        return f"""
[Config Warning]: ACA_POOL_MANAGEMENT_ENDPOINT not set. 
Skipping Dynamic Session execution. Here is the generated plan:

--- Generated Python Code ---
{generated_code}
-----------------------------
"""

if __name__ == "__main__":
    # Run with streamable-http transport — accepts POST at /mcp on 0.0.0.0:8001
    mcp.run(transport="streamable-http")
