import streamlit as st
 
def update_kb_ui():
    st.header("Trigger updating knowledge base")
 
    project_name = st.text_input("Project Name")
 
    repo_type = st.radio(
        "Repository Type",
        ["Source Code", "Test Automation Scripts"]
    )
 
    include_subfolders = st.text_input("Include Subfolders")
    include_files = st.text_input("Include Files")
 
    if st.button("Start Updating"):
        st.success("Knowledge base update triggered")
 
        st.json({
            "project": project_name,
            "repo_type": repo_type,
            "include_subfolders": include_subfolders,
            "include_files": include_files
        })
 