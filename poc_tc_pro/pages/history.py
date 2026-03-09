import streamlit as st
import sqlite3
import json

DB_FILE = "qa_history.db"


def get_qa_pairs(search_query=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    query = "SELECT id, api_key, kb_id, question, answer, retrieved_data FROM qa_pairs"
    params = []
    
    if search_query:
        query += " WHERE question LIKE ? OR answer LIKE ?"
        params = [f"%{search_query}%", f"%{search_query}%"]
    
    query += " ORDER BY id DESC"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    return [{"id": row[0], "api_key": row[1], "kb_id": row[2], "question": row[3], "answer": row[4], "retrieved_data": json.loads(row[5])} for row in rows]

st.set_page_config(page_title="Q&A History", layout="wide")

# Main content
st.title("Q&A History")

search_query = st.text_input("🔍 Search", key="search")

qa_pairs = get_qa_pairs(search_query)

for qa_pair in qa_pairs:
    with st.expander(qa_pair["question"][:50] + "..."):
        st.write("Question:", qa_pair["question"])
        st.write("Answer:", qa_pair["answer"])
        #st.write("API Key:", qa_pair["api_key"])
        #st.write("KB ID:", qa_pair["kb_id"])
        with st.expander("Retrieved Data"):
            st.json(qa_pair["retrieved_data"])

# Clear all Q&A pairs
if st.button("Clear All Q&A Pairs"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM qa_pairs")
    conn.commit()
    conn.close()
    st.success("All Q&A pairs cleared from the database!")
    st.experimental_rerun()

# Add a Home button to return to the main page
#if st.button("Back to Home"):
#    st.switch_page("ui_sample1/poc_ui2.py")  # or "Home.py" if that's your main file name