#for creating local file-based db table 

import sqlite3

DB_FILE = "qa_history.db"

def reset_table():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS qa_pairs;")
    conn.commit()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS qa_pairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT,
            kb_id TEXT,
            question TEXT,
            answer TEXT,
            retrieved_data TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            api_calls INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("Table 'qa_pairs' recreated with the new schema ✅")

if __name__ == "__main__":
    reset_table()