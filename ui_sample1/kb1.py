#feat: Add token, api calls in kb

import requests
import uuid
import os
import json
from dotenv import load_dotenv
 
load_dotenv()
 
API_KEY = os.getenv("GEP_API_KEY")
WORKSPACE_ID = os.getenv("kb_id")
MODEL_NAME = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
 
def query_with_rag(prompt, API_KEY, WORKSPACE_ID, MODEL_NAME):
    url = "https://api.generative.engine.capgemini.com/v2/llm/invoke"
 
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
 
    payload = {
        "action": "run",
        "modelInterface": "multimodal",
        "adapterInterfaceVersion": "v2",
        "data": {
            "mode": "chain",
            "text": prompt,
            "files": [],
            "modelName": MODEL_NAME,
            "provider": "bedrock",
            "sessionId": str(uuid.uuid4()),
            "workspaceId": WORKSPACE_ID,
            "modelKwargs": {
                "maxTokens": 1024,
                "temperature": 0.5,
                "streaming": False,
                "topP": 0.3
            },
            "ragKwargs": {
                "docLimit": 10
            }
        }
    }
 
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
 
    #print("Raw API response:", json.dumps(result, indent=2))
 
    # -----------------------------
    # FIXED TOKEN EXTRACTION
    # -----------------------------
    metadata = result.get("metadata", {})
    usage = metadata.get("usage", {})
 
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
 
    # -----------------------------
    # Extract content
    # -----------------------------
    content = result.get("content", "")
    retrieved_docs = metadata.get("documents", [])
 
    return {
        "content": content,
        "retrieved_documents": retrieved_docs,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "api_calls": 1
    }