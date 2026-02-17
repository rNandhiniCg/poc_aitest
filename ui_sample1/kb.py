import requests
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("api_key")
WORKSPACE_ID =os.getenv( "kb_id")
MODEL_NAME = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

def query_with_rag(prompt,API_KEY,WORKSPACE_ID,MODEL_NAME):
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
               "temperature": 0.6,
               "streaming": False,
               "topP": 0.9
           },
           "ragKwargs": {
               "docLimit": 10,
               #"knowledgeBaseIds":[WORKSPACE_ID]
           }
       }
   }
   response = requests.post(url, headers=headers, json=payload)
   
   return response.json()