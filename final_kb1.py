#KB code - openai gpt-5 model

import requests
import uuid
import os 
from dotenv import load_dotenv

load_dotenv()

GEP_API_KEY = os.getenv("GEP_API_KEY")
kb_id = os.getenv("kb_id")
#from config import WORKSPACE_ID, API_KEY
 
def query_rag_with_kb(api_key, workspace_id, prompt, model_name):
   
    url = "https://api.generative.engine.capgemini.com/v2/llm/invoke"
   
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
   
    payload = {
        "action": "run",
        "modelInterface": "langchain",
        "data": {
            "mode": "chain",
            "text": prompt,
            "files": [],
            "modelName": model_name,            
            "provider": "azure",
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

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        return None
 
# Example usage
if __name__ == "__main__":
    api_key = GEP_API_KEY
    model_name = "openai.gpt-5.2"
    workspace_id = kb_id

    prompt = input("Ask your question: ")
    print("\nGenerating response ...")

    result = query_rag_with_kb(api_key, workspace_id, prompt, model_name)

    #print(result)
    print(result["content"])
    #print(json.dumps(result, indent=2))
    