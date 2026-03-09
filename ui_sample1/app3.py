#app3.py - same as app2.py
#rag_prompt - for all filetypes, Sh prompt

import streamlit as st # type: ignore
from kb import query_with_rag
import os
from dotenv import load_dotenv  # type: ignore
import sqlite3
import re
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

def parse_response(response):
    parts = response.split('```json')
    diff_json = json.loads(parts[1].split('```')[0]) if len(parts) > 1 else None
    dependencies_json = json.loads(parts[2].split('```')[0]) if len(parts) > 2 else None
    
    # Look for the test case table
    test_cases = "No appropriate Testcases found"
    if "| Test Case ID | Priority | Relevant For | Remarks |" in response:
        table_start = response.index("| Test Case ID | Priority | Relevant For | Remarks |")
        table_end = response.find("\n\n", table_start)
        test_cases = response[table_start:table_end].strip()
    
    return diff_json, dependencies_json, test_cases

st.set_page_config(page_title="AI-RAG LLM Q&A")
st.title("AI-Based Testcase Prioritzation")

if st.sidebar.button("History"):
    st.switch_page("pages/history.py")

#st.write(f"Model :  {MODEL_NAME}")

#old_files = st.text_area("Enter old source file name(s)", height=20, placeholder="Enter file name(s) separated by commas...")
new_files = st.text_area("Enter modified source file name(s)", height=60, placeholder="Enter file name(s) separated by commas...")
#test_scripts = st.text_area("Enter test script file name(s) (optional)", height=60, placeholder="Enter file name(s) separated by commas...")


if st.button("Prioritize TestCases"):
    if not new_files:
        st.warning("Please enter source code file name(s).", icon="⚠️")
    else:
        with st.spinner("Thinking..."):

          prompt= f"""
          
          New files: {new_files}
         

Compare the given files and prioritize test cases based on the changes.

"""
        
          rag_prompt = f"""
Use ONLY information retrieved from the Knowledge Base.
Task:
 1.The user will provide an updated filename. Your task is to automatically find
the correct original file from the Knowledge Base.
 
Rules to match files:
a. Normalize the user filename:
   - Remove words like "copy", "new", "final", "updated", "(1)", version numbers, etc.
   - Remove extra symbols and noisy suffixes.
   - Extract the core filename without extension.
 
b. Find the closest matching file in the Knowledge Base:
   Priority:
   a) Exact base name match (highest priority)
   b) Prefix match (e.g., "ospf6_neighbor" matches "ospf6_neighbor.c")
   c) Highest similarity score between filenames
   d) If still multiple matches → choose the shortest filename (likely the real module file)
 
Compare the given files to knowledge Base Files and return STRICT structured output.
 
Files:
{prompt}
 
Instructions:
1) Generate exact diff between old and new file.
   Output ONLY in JSON key-value structured format.
   Rules:
   output format(STRICT):
   {{
  "added_functions": [],
  "modified_functions": [],
  "deleted_functions": [],
  "changes": {{
    ""
  }}
}}
 
2) After diff, generate dependencies ONLY in JSON.
 Rules:
 Output Format (STRICT):
[
  {{
    "Function": "",
    "Internal_calls": [],
    "Testcase_id_internal": "",
    "External_calls": [],
    "Testcase_id_external": "",
    "Testcase_files": []
  }}
 
3) After dependencies, find relevant test cases in table format:
 
Test Case ID | Priority | Relevant For | Remarks
 
Rules:
High Priority: The function is newly added.
Medium Priority: The function internally calls another function defined in the same file.
Low Priority: The function calls a function from an external file or module.
- If none → return "No relevant testcases available"
 
Return output in this exact order:
1. Diff JSON
2. Dependencies JSON
3. Relevant Test Cases Table
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

                input_tokens = result.get("input_tokens", 0)
                output_tokens = result.get("output_tokens", 0)
                api_calls = result.get("api_calls", 0)
                
                # Update total API calls
                global total_api_calls
                # Add a global variable to track total API calls
                total_api_calls = 0
                total_api_calls += api_calls

                st.session_state.last_qa_pair = {
                   "api_key": API_KEY,
                   "kb_id": WORKSPACE_ID,
                   "question": prompt,
                   "answer": answer,
                   "retrieved_data": retrieved_data,
                   "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "api_calls": api_calls
                }
               
                diff_json, dependencies_json, test_cases = parse_response(answer)
               
                st.success("Response", icon="✅")
                st.markdown("### Prioritized TestCases")
                if "| Test Case ID |" in test_cases:
                    st.markdown(test_cases)
                else:
                    st.write(test_cases)
               
                with st.expander("Explain Testcase Selection"):
                    st.subheader("Diff JSON")
                    st.json(diff_json)
                    st.subheader("Dependencies JSON")
                    st.json(dependencies_json)

                    # Display API call and token information
                    st.subheader("API Usage Information")
                    st.write(f"API Calls: {api_calls}")
                    st.write(f"Total API Calls: {total_api_calls}")
                    st.write(f"Input Tokens: {input_tokens}")
                    st.write(f"Output Tokens: {output_tokens}")
                    st.write(f"Total Tokens: {input_tokens + output_tokens}")
        else:
               st.error("Unexpected response", icon="🚨")
               st.json(result)

if st.button("Save to History"):
    if hasattr(st.session_state, 'last_qa_pair'):
        qa_pair = st.session_state.last_qa_pair
        store_qa_pair(qa_pair["api_key"], qa_pair["kb_id"], qa_pair["question"], qa_pair["answer"], qa_pair["retrieved_data"])
        st.success("Q&A pair stored successfully!")
        st.info("Click on 'History' in the sidebar to view stored Q&A pairs.")
    else:
        st.warning("No Q&A pair available to store. Generate a response first.", icon="⚠️")