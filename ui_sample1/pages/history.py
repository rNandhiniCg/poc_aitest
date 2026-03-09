#Displaying Q&A , Metadata (API calls, tokens count), Retrieved data

import streamlit as st
import sqlite3
import json

DB_FILE = "qa_history.db"

# ---- Fetch rows with all metadata ----
def get_qa_pairs(search_query=None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    query = """
        SELECT 
            id, 
            api_key, 
            kb_id, 
            question, 
            answer, 
            retrieved_data,
            input_tokens,
            output_tokens,
            api_calls,
            created_at
        FROM qa_pairs
    """
    params = []

    if search_query:
        query += " WHERE question LIKE ? OR answer LIKE ?"
        params = [f"%{search_query}%", f"%{search_query}%"]

    query += " ORDER BY id DESC"

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    qa_list = []
    for row in rows:
        qa_list.append({
            "id": row[0],
            "api_key": row[1],
            "kb_id": row[2],
            "question": row[3],
            "answer": row[4],
            "retrieved_data": json.loads(row[5]) if row[5] else {},
            "input_tokens": row[6],
            "output_tokens": row[7],
            "api_calls": row[8],
            "created_at": row[9],
        })
    return qa_list


# ---- UI ----
st.set_page_config(page_title="Q&A History", layout="wide")
st.title("Q&A History")

search_query = st.text_input("🔍 Search", key="search")

qa_pairs = get_qa_pairs(search_query)

if not qa_pairs:
    st.info("No matching results found.")
else:
    for qa in qa_pairs:
        with st.expander(f"#{qa['id']} — {qa['question'][:60]}..."):
            st.subheader("Question")
            st.write(qa["question"])

            st.subheader("Answer")
            st.write(qa["answer"])

            # ---- ADDED: METADATA ----
            with st.expander("Metadata"):
                st.write(f"**API Calls:** {qa['api_calls']}")
                st.write(f"**Input Tokens:** {qa['input_tokens']}")
                st.write(f"**Output Tokens:** {qa['output_tokens']}")
                st.write(f"**Total Tokens:** {qa['input_tokens'] + qa['output_tokens']}")
                st.caption(f"Created at: {qa['created_at']}")

            with st.expander("Retrieved Data"):
                st.json(qa["retrieved_data"])

            


# ---- CLEAR ALL ----
if st.button("Clear All Q&A Pairs"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM qa_pairs")
    conn.commit()
    conn.close()
    st.success("All Q&A pairs cleared!")
    st.experimental_rerun()