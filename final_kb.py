import requests
import json
import uuid

import os 
from dotenv import load_dotenv
load_dotenv()

GEP_API_KEY= os.getenv("GEP_API_KEY")

kb_id= os.getenv("kb_id")
 
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
    return response.json()
 

api_key = GEP_API_KEY
model_name="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
workspace_id = kb_id

prompt = input("Ask your question: ")
print("Generating response ...")

result = query_with_rag(api_key, workspace_id, prompt, model_name)
#print(json.dumps(result, indent=2))
print(result["content"])

