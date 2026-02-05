import streamlit as st
from ui.build_kb import build_kb_ui
from ui.update_kb import update_kb_ui
from ui.find_tests import find_tests_ui
 
st.set_page_config(page_title="AI Testcase Prioritization", layout="wide")
 
st.title("AI-based Test Case Prioritization")
 
menu = st.sidebar.radio(
    "Select Workflow",
    [
        "Build Knowledge Base",
        "Update Knowledge Base",
        "Find Prioritized Test Cases"
    ]
)
 
if menu == "Build Knowledge Base":
    build_kb_ui()
elif menu == "Update Knowledge Base":
    update_kb_ui()
elif menu == "Find Prioritized Test Cases":
    find_tests_ui()