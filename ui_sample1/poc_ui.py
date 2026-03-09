import os
import json
import sqlite3
from dotenv import load_dotenv

import streamlit as st
from tinydb import TinyDB, Query

# ---- External RAG function ----

from kb1 import query_with_rag

# ------------------ ENV & CONFIG -------------------
load_dotenv()

API_KEY = os.getenv("GEP_API_KEY1")
WORKSPACE_ID = os.getenv("kb_id3")
MODEL_NAME = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"   # as in app.py

# Optional (only used if you later enable "Save to History")
DB_FILE = "qa_history.db"


# ----------------- HELPERS (from app.py) -----------------
def parse_response(response: str):
    """
    Parses the model response in the same way as app.py:
    - It expects 3 sections in a strict order:
      1) ```json ...```  -> Diff JSON
      2) ```json ...```  -> Dependencies JSON
      3) Markdown table   -> Test Cases table
    """
    parts = response.split('```json')

    # Diff JSON
    try:
        diff_json = json.loads(parts[1].split('```')[0]) if len(parts) > 1 else None
    except json.JSONDecodeError:
        diff_json = None
        st.error("Error parsing diff JSON. The response format may be incorrect.")

    # Dependencies JSON
    try:
        dependencies_json = json.loads(parts[2].split('```')[0]) if len(parts) > 2 else None
    except json.JSONDecodeError:
        dependencies_json = None
        st.error("Error parsing dependencies JSON. The response format may be incorrect.")

    # Test case table (as markdown)
    test_cases = "No appropriate Testcases found"
    # Search robustly for the header row
    header_variants = [
        "| Test Case ID | Priority | Relevant For | Remarks |",
        "Test Case ID | Priority | Relevant For | Remarks",
        "|Test Case ID|Priority|Relevant For|Remarks|"
    ]
    table_start = -1
    for hv in header_variants:
        if hv in response:
            table_start = response.index(hv)
            break

    if table_start != -1:
        # Find end of table by a blank line or end of text
        table_end = response.find("\n\n", table_start)
        if table_end == -1:
            table_end = len(response)
        test_cases = response[table_start:table_end].strip()

    return diff_json, dependencies_json, test_cases

def has_valid_qa(qa: dict | None) -> bool:
    """
    Ensure we actually have a RAG result to save.
    Requires non-empty 'question' and 'answer' strings.
    """
    if not qa or not isinstance(qa, dict):
        return False
    question = (qa.get("question") or "").strip()
    answer = (qa.get("answer") or "").strip()
    return bool(question) and bool(answer)

def run_prioritization_with_rag(new_files: str):
    """
    Call the RAG backend using your app.py logic and return parsed artifacts.
    Returns:
      {
        "ok": bool,
        "answer": str,
        "diff_json": dict|None,
        "dependencies_json": dict|list|None,
        "test_cases_md": str,
        "input_tokens": int,
        "output_tokens": int,
        "api_calls": int,
        "retrieved_data": list
      }
    """
    prompt = f"""
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
    ]

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

    # Defensive defaults
    input_tokens = result.get("input_tokens", 0)
    output_tokens = result.get("output_tokens", 0)
    api_calls = result.get("api_calls", 0)
    retrieved_data = result.get("retrieved_documents", [])

    if "content" not in result:
        return {
            "ok": False,
            "answer": "",
            "diff_json": None,
            "dependencies_json": None,
            "test_cases_md": "",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "api_calls": api_calls,
            "retrieved_data": retrieved_data
        }

    answer = result["content"]

    try:
        diff_json, dependencies_json, test_cases = parse_response(answer)
    except Exception as e:
        st.error(f"Error parsing response: {str(e)}")
        st.text(answer)  # Raw output to debug
        diff_json, dependencies_json, test_cases = None, None, "No appropriate Testcases found"

    return {
        "ok": True,
        "answer": answer,
        "diff_json": diff_json,
        "dependencies_json": dependencies_json,
        "test_cases_md": test_cases,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "api_calls": api_calls,
        "retrieved_data": retrieved_data
    }


# Store to history.py
def store_qa_pair(api_key, kb_id, question, answer, retrieved_data,
                  input_tokens=0, output_tokens=0, api_calls=0):
    """Insert a single QA record with token and API usage stats."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO qa_pairs (api_key, kb_id, question, answer, retrieved_data, input_tokens, output_tokens, api_calls)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (api_key, kb_id, question, answer, json.dumps(retrieved_data), input_tokens, output_tokens, api_calls))
    conn.commit()
    conn.close()


# ------------------ MAIN UI (your original) ------------------
# If you want a page title on the browser tab (safe to keep)
st.set_page_config(page_title="Test Case Prioritization Utility")

# Sidebar History 
if st.sidebar.button("History"):
    #create pages/history.py for a Streamlit multipage app and navigate here:
    st.switch_page("pages/history.py")

# --- DB init ---
db = TinyDB(r"C:\Users\NANRAMAS\OneDrive - Capgemini\Documents\Poc_demo\ai_test3\ui_sample1\data\project_onboarding.json")

# --- Header & Logo ---
st.image(r"C:\Users\NANRAMAS\OneDrive - Capgemini\Documents\Poc_demo\ai_test3\ui_sample1\data\CG_Cisco_Logo.png")
st.header("Test Case Prioritization Utility", text_alignment="center")

list_tab, onboard_tab, select_tab, prioritze_tab = st.tabs(
    ["List Projects", "Onboard Project", "Select Project", "Find Prioritized Test Cases"]
)

with list_tab:
    db_records = db.all()
    st.table(db_records)

with onboard_tab:
    project = st.text_input("Project Name")
    source_code_repo = st.text_input("Source Code Repo")
    test_script_repo = st.text_input("Test Scripts Repo")
    if st.button("Onboard"):
        if project and source_code_repo and test_script_repo:
            db.insert({
                "Project": project,
                "SourceCodeRepo": source_code_repo,
                "TestScriptRepo": test_script_repo
            })
            st.success(f"Project '{project}' onboarded.")

            # RESET FIELDS HERE
            st.session_state["project"] = ""
            st.session_state["source_code_repo"] = ""
            st.session_state["test_script_repo"] = ""

        else:
            st.warning("Please fill all fields.")

with select_tab:
    db_records = db.all()
    project_list = [project["Project"] for project in db_records] if db_records else []
    project = st.pills("Select Project ", project_list) if project_list else None
    if not project_list:
        st.info("No projects found. Please onboard a project first.")

with prioritze_tab:
    # Remember selected project if any
    #if project is not None:
    #    st.subheader("Project : " + project, text_alignment="center")

    # State for API usage accumulation
    if 'total_api_calls' not in st.session_state:
        st.session_state.total_api_calls = 0
    if 'last_qa_pair' not in st.session_state:
        st.session_state.last_qa_pair = None
    if 'prev_choice' not in st.session_state:
        st.session_state.prev_choice = None
    if 'prev_input' not in st.session_state:
        st.session_state.prev_input = None

    diff_file_name = ""
    choice = st.pills(
        "Find prioritized test cases using one of these options",
        ["For given Defect ID(s)", "For given Diff file(s)", "For diff files contained in a folder", "For given modified file(s)"],
        default="For given Defect ID(s)"
    )

    choice_value_dict = {
        "For given Defect ID(s)": "Enter Defect ID(s) separated by comma",
        "For given Diff file(s)": "Enter path of the diff file",
        "For diff files contained in a folder": "Enter path of the folder containing diff files",
        "For given modified file(s)": "Enter modified src filename "
    }

    #value = st.text_input("Input", placeholder=choice_value_dict[choice])
    value = st.text_input("Input", placeholder=choice_value_dict[choice], key="input_value")

    # Clear previous QA result if the user changed the choice or input text
    if st.session_state.prev_choice != choice or st.session_state.prev_input != st.session_state.input_value:
        st.session_state.last_qa_pair = None

        # Keep for the next rerun comparison
    st.session_state.prev_choice = choice
    st.session_state.prev_input = st.session_state.input_value

    # Normalize input variables by choice
    defect_id = folder_name = modified_filename = None
    match choice:
        case "For given Defect ID(s)":
            defect_id = value
        case "For given Diff file(s)":
            diff_file_name = value
        case "For diff files contained in a folder":
            folder_name = value
        case "For given modified file(s)":
            modified_filename = value

    # ---- The button that should trigger RAG logic ----
    if st.button("Find Prioritized Test cases"):
        # Route by choice; your earlier file-reading behavior is kept for Diff file(s)
        if choice == "For given Diff file(s)":
            # Backward compatible behavior you had earlier
            if diff_file_name == "":
                diff_file_name = "diff1.txt"
            try:
                with open(diff_file_name, "r") as file:
                    content = file.read()
                    st.write(content)
            except FileNotFoundError:
                st.error("File Not Found")

        elif choice == "For given modified file(s)":
            if not modified_filename:
                st.warning("Please enter modified source filename(s).", icon="⚠️")
            else:
                with st.spinner("Thinking..."):
                    result = run_prioritization_with_rag(modified_filename)

                # Update total API calls (like in app.py)
                st.session_state.total_api_calls += result.get("api_calls", 0)

                if not result["ok"]:
                    st.error("Unexpected response", icon="🚨")
                    st.json(result)  # show the raw for debugging
                else:
                    # SUCCESS UI (same semantics as app.py)
                    st.success("Response", icon="✅")
                    st.markdown("### Prioritized TestCases")
                    tc_md = result["test_cases_md"]
                    if "| Test Case ID |" in tc_md or "Test Case ID | Priority" in tc_md:
                        st.markdown(tc_md)
                    else:
                        st.write(tc_md)

                    with st.expander("Explain Testcase Selection"):
                        st.subheader("Diff JSON")
                        st.json(result["diff_json"])
                        st.subheader("Dependencies JSON")
                        st.json(result["dependencies_json"])

                        # Display API call and token info
                        with st.expander("Metadata info"):
                        #st.subheader("API Usage Information")
                            st.write(f"API Calls (this call): {result.get('api_calls', 0)}")
                            st.write(f"Total API Calls: {st.session_state.total_api_calls}")
                            st.write(f"Input Tokens: {result.get('input_tokens', 0)}")
                            st.write(f"Output Tokens: {result.get('output_tokens', 0)}")
                            st.write(f"Total Tokens: {result.get('input_tokens', 0) + result.get('output_tokens', 0)}")

                    
                # --- Capture "last QA" for Save to History
                    st.session_state.last_qa_pair = {
                        "api_key": API_KEY,
                        "kb_id": WORKSPACE_ID,
                        "question": result.get(
                                "question",
                                f"New files: {modified_filename}\nCompare the given files and prioritize test cases based on the changes."
                            ),

                        "answer": result["answer"],
                        "retrieved_data": result.get("retrieved_data", []),
                        "input_tokens": result.get("input_tokens", 0),
                        "output_tokens": result.get("output_tokens", 0),
                        "api_calls": result.get("api_calls", 0)
                    }


                

        elif choice == "For diff files contained in a folder":
            st.info("Folder-based diff processing is not implemented yet in this UI. Provide a single diff file or modified file(s).")

        elif choice == "For given Defect ID(s)":
            st.info("Defect-ID based prioritization is not implemented in this UI. Use 'For given modified file(s)' for RAG-based results.")

    
    
# ---- Save To History ----
    can_save = has_valid_qa(st.session_state.get("last_qa_pair"))

            # Disable the button when there's nothing valid to save
    if st.button("Save to History", disabled=not can_save, help=None if can_save else "Run 'Find Prioritizd Test cases' first"):

                qa_pair = st.session_state.last_qa_pair
                try:
                    store_qa_pair(   
                        qa_pair["api_key"], # type: ignore
                        qa_pair["kb_id"],
                        qa_pair["question"],
                        qa_pair["answer"],
                        qa_pair["retrieved_data"],
                        qa_pair.get("input_tokens", 0),
                        qa_pair.get("output_tokens", 0),
                        qa_pair.get("api_calls", 0),
                    
                    )
                    st.success("Q&A pair stored successfully!")
                    st.info("Click on 'History' in the sidebar to view stored Q&A pairs.")
                except Exception as e:
                    st.error(f"Failed to store Q&A pair: {e}")       

# Close DB when script completely ends (Streamlit reruns; TinyDB handles safely)
# db.close()   # Optional: TinyDB often doesn't require explicit close per rerun