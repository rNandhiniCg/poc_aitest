#app2.py - ui update add hide json expander , display only TC table
#rag_prompt - for all filetypes

import streamlit as st
from kb import query_with_rag
import os
from dotenv import load_dotenv
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
You are a senior software engineer.
 
Use ONLY information retrieved from the Knowledge Base.
Do NOT assume missing content.
 
Task:
Compare the given files and return STRICT structured output.
 
Files:
{prompt}
 
----------------------------------------
LANGUAGE-AWARE ANALYSIS
----------------------------------------
 
The files may be written in:
- Python (.py)
- C (.c, .h)
- C++ (.cpp, .hpp)
- Java (.java)
 
Detect language automatically based on file extension and apply appropriate rules.
 
----------------------------------------
1) Generate exact diff between old and new file.
Output ONLY in JSON format:
 
{{
  "fileType": "python | c | cpp | java",
  "keyChanges": {{
    "added": {{
      "classes": [],
      "functions": [],
      "methods": [],
      "structs": [],
      "macros": [],
      "imports": [],
      "functionality": []
    }},
    "modified": {{
      "entity_name": {{
        "added": "",
        "removed": ""
      }}
    }},
    "removed": {{
      "classes": [],
      "functions": [],
      "methods": [],
      "structs": [],
      "macros": []
    }}
  }},
  "detailedChanges": {{
    "entity_name": {{
      "type": "class | function | method | struct | macro",
      "change": "exact structural change summary"
    }}
  }}
}}
 
Rules:
- For C/C++ → focus on functions, structs, macros, headers.
- For Java → focus on classes, methods, imports.
- For Python → focus on classes, methods, functions, imports.
- If incomplete file content → return:
  "Insufficient data in Knowledge Base"
 
No explanations outside JSON.
 
----------------------------------------
2) Generate dependencies ONLY in JSON:
 
{{
  "dependencies": {{
    "functions_called": [],
    "struct_usage": [],
    "class_usage": [],
    "header_includes": [],
    "imports": []
  }}
}}
 
Rules:
- For C/C++ → include #include headers and called functions.
- For Java → include imported classes and method calls.
- For Python → include imports and function/class usage.
- Do NOT guess dependencies.
 
----------------------------------------
3) Find relevant test cases.
 
Testcase Search Rules:
 
- If specific test scripts are mentioned in retrieved context,
  search ONLY in those test files.
 
- If not mentioned,
  search across ALL available test scripts.
 
- If no testcases found, return EXACT:
  "No appropriate Testcases found"
 
Priority:
- Priority 1 → Directly impacted
- Priority 2 → Dependency impacted
 
Return STRICT table:
 
| Test Case ID | Priority | Relevant For | Remarks |
 
No extra explanation.
 
----------------------------------------
Return output in this order ONLY:
1. Diff JSON
2. Dependencies JSON
3. Relevant Test Cases Table OR exact message
----------------------------------------
 
STRICT MODE:
No markdown explanation.
No summary.
Only structured output.
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