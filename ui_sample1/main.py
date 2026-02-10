import streamlit as st
from kb import query_with_rag
import os
from dotenv import load_dotenv
import sqlite3
import json

load_dotenv()

API_KEY = os.getenv("GEP_API_KEY")
WORKSPACE_ID = os.getenv("kb_id")
MODEL_NAME = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
DB_FILE = "qa_history.db"

def store_qa_pair(api_key, kb_id, question, answer, retrieved_data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO qa_pairs (api_key, kb_id, question, answer, retrieved_data) 
        VALUES (?, ?, ?, ?, ?)
    """, (api_key, kb_id, question, answer, json.dumps(retrieved_data)))
    conn.commit()
    conn.close()

st.set_page_config(page_title="RAG LLM Demo")
st.title("RAG LLM Q&A")

# Add a History button to the sidebar
if st.sidebar.button("History"):
    st.switch_page("pages/history.py")

prompt = st.text_area(
   "Ask your question",
   height=120,
   placeholder="Type your question here..."
)

if st.button("Generate"):
   if not prompt:
       st.warning("Please enter a question", icon="⚠️")
   else:
       with st.spinner("Thinking..."):
           rag_prompt = f"""
           You are a senior Python engineer.
Use ONLY the information retrieved from the Knowledge Base.
Context:
The knowledge base contains multiple versions of an OSPF Python implementation.
Task:
{prompt}
Instructions:
- Compare old and new versions of the OSPF code
- Identify logic differences
- Highlight added or removed functionality
- If relevant information is missing, clearly say so
"""
           
           result = query_with_rag(
               rag_prompt,
               API_KEY,
               WORKSPACE_ID,
               MODEL_NAME
           )
           
           if "content" in result:
               answer = result["content"]
               retrieved_data = result.get("retrieved_documents", [])
               
               st.session_state.last_qa_pair = {
                   "api_key": API_KEY,
                   "kb_id": WORKSPACE_ID,
                   "question": prompt,
                   "answer": answer,
                   "retrieved_data": retrieved_data
               }
               
               st.success("Response", icon="✅")
               st.write(answer)
           else:
               st.error("Unexpected response", icon="🚨")
               st.json(result)

if st.button("Store Last Q&A Pair"):
    if hasattr(st.session_state, 'last_qa_pair'):
        qa_pair = st.session_state.last_qa_pair
        store_qa_pair(qa_pair["api_key"], qa_pair["kb_id"], qa_pair["question"], qa_pair["answer"], qa_pair["retrieved_data"])
        st.success("Q&A pair stored successfully!")
        st.info("Click on 'History' in the sidebar to view stored Q&A pairs.")
    else:
        st.warning("No Q&A pair available to store. Generate a response first.", icon="⚠️")