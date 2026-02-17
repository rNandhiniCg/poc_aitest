#app1.py - streamlit ui + llm kb logic

import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv
 
# Load env variables
load_dotenv()
 
GEP_API_KEY = os.getenv("GEP_API_KEY")
KB_ID = os.getenv("kb_id")

# Model 
model_name = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
 
# ---------- LLM + RAG FUNCTION ----------
def query_with_rag(api_key, workspace_id, prompt, model_name):
    url = "https://api.generative.engine.capgemini.com/v2/llm/invoke"
 
    headers = {
        "x-api-key": GEP_API_KEY,
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
 
# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="RAG Chatbot", layout="wide")
 
st.title("AI-based Test Case Prioritization")
st.caption(f"Model : {model_name}  \" via Capgemini GEP")
 
# Input box
user_question = st.text_area(
    "Ask your question",
    height=120,
    placeholder="Type your question here..."
)
 

 
# Submit button
if st.button("Generate Answer"):
    if not user_question.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("Generating response..."):
            try:
                result = query_with_rag(
                    api_key=GEP_API_KEY,
                    workspace_id=KB_ID,
                    prompt=user_question,
                    model_name=model_name
                )
 
                # Display response safely
                if "content" in result:
                    st.markdown("### Assistant's Response")
                    st.write(result["content"])
                else:
                    st.error("Unexpected response format")
                    st.json(result)
 
            except Exception as e:
                st.error(f"Error: {e}")