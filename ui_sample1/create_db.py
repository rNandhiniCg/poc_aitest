import sqlite3

DB_FILE = "qa_history.db"

def create_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS qa_pairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_key TEXT NOT NULL,
        kb_id TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        retrieved_data TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database '{DB_FILE}' created successfully with 'qa_pairs' table.")

if __name__ == "__main__":
    create_database()