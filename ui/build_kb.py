import streamlit as st
 
def build_kb_ui():
    st.header("Trigger building knowledge base")
 
    project_name = st.text_input("Project Name")
 
    repo_type = st.radio(
        "Repository Type",
        ["Source Code", "Test Automation Scripts"]
    )
 
    input_type = st.radio(
        "Input Source",
        ["GitHub Link", "Local Repo"]
    )
 
    if input_type == "GitHub Link":
        repo_path = st.text_input("GitHub Link")
    else:
        repo_path = st.text_input("Local Repository Path")
 
    include_subfolders = st.text_input("Include Subfolders (comma separated)")
    exclude_subfolders = st.text_input("Exclude Subfolders (comma separated)")
 
    if st.button("Start Building"):
        st.success("Knowledge base build triggered")
 
        st.json({
            "project": project_name,
            "repo_type": repo_type,
            "repo_path": repo_path,
            "include": include_subfolders,
            "exclude": exclude_subfolders
        })
 