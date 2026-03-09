#original poc_ui version

import streamlit as st
from tinydb import TinyDB, Query

db = TinyDB(r"C:\Users\NANRAMAS\OneDrive - Capgemini\Documents\Poc_demo\ai_test3\ui_sample1\data\project_onboarding.json")
st.image(r"C:\Users\NANRAMAS\OneDrive - Capgemini\Documents\Poc_demo\ai_test3\ui_sample1\data\CG_Cisco_Logo.png")
st.header("Test Case Prioritization Utility", text_alignment="center")
list_tab, onboard_tab, select_tab, prioritze_tab = st.tabs(
     ["List Projects",
      "Onboard Project", 
      "Select Project", 
      "Find Prioritized Test Cases"])
with list_tab:   
    db_records = db.all()
    st.table(db_records)

with onboard_tab:
    project = st.text_input("Project Name")
    source_code_repo = st.text_input("Source Code Repo")
    test_script_repo = st.text_input("Test Scripts Repo")
    if st.button("Onboard"):
        db.insert({"Project":project, 
                    "SourceCodeRepo":source_code_repo,
                    "TestScriptRepo":test_script_repo})
with select_tab:
    db_records = db.all()
    project_list = [project["Project"] for project in db_records]
    project = st.pills("Select Project ", project_list)

with prioritze_tab:
    if project != None:
        st.subheader("Project : " + project, text_alignment="center")
    diff_file_name = ""
    choice = st.pills("Find prioritized test cases using one of these options", 
                      ["For given Defect ID(s)", "For given Diff file(s)", "For diff files contained in a folder", "For given modified file(s)"], 
                      default="For given Defect ID(s)")
    choice_value_dict = {"For given Defect ID(s)":"Enter Defect ID(s) separated by comma",
                         "For given Diff file(s)":"Enter path of the diff file",
                         "For diff files contained in a folder":"Enter path of the folder containing diff files",
                         "For given modified file(s)":"Enter modified src filename "}
          
    value = st.text_input("Input", placeholder= choice_value_dict[choice])

    match (choice):
        case "For given Defect ID(s)":
              defect_id = value
        case "For given Diff file(s)":
              diff_file_name = value
        case "FFor diff files contained in a folder":
              folder_name = value
        case "For given modified file(s)":
              modified_filename = value

    if st.button("Find Prioritizd Test cases"):
        if diff_file_name == "":
            diff_file_name = "diff1.txt"
        try:
                with open(diff_file_name, "r") as file:
                    content = file.read()
                    st.write(content)
                    file.close()
        except FileNotFoundError:
                st.error("File Not Found")

db.close()