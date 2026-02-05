import streamlit as st
import pandas as pd
import time
 
def find_tests_ui():
    st.header("Find Prioritized Test Cases for a given diff")
 
    project_name = st.text_input("Project Name")
    defect_id = st.text_input("Defect ID / JIRA ID")
    diff_path = st.text_input("Diff File / Folder having diffs")
 
    if st.button("Find Prioritized Test Cases"):
        
# Create a placeholder for the temporary status message
        msg = st.empty()
        msg.success("Fetching prioritized test cases..")

        # --- Your actual compute/fetch code goes here ---
        # Simulate work
        time.sleep(2)

        # Dummy output (later from RAG + LLM)
        data = [
            [1, "TC_Login_001", "http://testcase/1", "Directly impacted"],
            [2, "TC_Auth_010", "http://testcase/2", "Near to diff"],
            [3, "TC_UI_021", "http://testcase/3", "Somewhat impacted"]
        ]

        # Clear the success message
        msg.empty()

        df = pd.DataFrame(
            data,
            columns=["Seq#", "Test Case#", "URL", "Remarks"]
        )

        # Show the results table
        st.divider()
        st.table(df)