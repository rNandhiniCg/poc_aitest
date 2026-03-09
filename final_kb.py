#kb code - anthropic.claude-3-7-sonnet model

import requests
import json
import uuid
import os 
from dotenv import load_dotenv

load_dotenv()

GEP_API_KEY = os.getenv("GEP_API_KEY")
kb_id = os.getenv("kb_id")

def query_with_rag(api_key, workspace_id, prompt, model_name):
    url = "https://api.generative.engine.capgemini.com/v2/llm/invoke"
   
    headers = {
        "x-api-key": api_key,
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
            "modelName": model_name,
            "provider": "bedrock",
            "sessionId": str(uuid.uuid4()),
            "workspaceId": workspace_id,  
            "modelKwargs": {
                "maxTokens": 1024,
                "temperature": 0.6,
                "streaming": False,
                "topP": 0.9
            },
            "ragKwargs": {
                "docLimit": 10  
            }
        }
    }
   
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    
    # Extract relevant information
    content = result.get("content", "")
    retrieved_documents = result.get("retrievedDocuments", [])
    
    # Extract token counts if available
    usage = result.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    
    return {
        "content": content,
        "retrieved_documents": retrieved_documents,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "api_calls": 1,
        "full_response": result  # Include full response for debugging
    }

api_key = GEP_API_KEY
model_name = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
workspace_id = kb_id

prompt = input("Ask your question: ")
print("Generating response ...")

result = query_with_rag(api_key, workspace_id, prompt, model_name)

print("Content:")
print(result["content"])
'''
print("\nRetrieved Documents:")
for doc in result["retrieved_documents"]:
    print(json.dumps(doc, indent=2))

print(f"\nInput tokens: {result['input_tokens']}")
print(f"Output tokens: {result['output_tokens']}")
print(f"API calls: {result['api_calls']}")

print("\nFull API Response:")
print(json.dumps(result['full_response'], indent=2))
'''