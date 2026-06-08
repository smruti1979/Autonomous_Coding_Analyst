import sqlite3
import os

DB_FILE = "analysis_history.db"

def init_db():
    """Initializes the SQLite database and creates the permanent output storage table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_results (
            job_id TEXT PRIMARY KEY,
            user_id TEXT,
            prompt TEXT,
            status TEXT,
            ai_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("🗄️ [Database System] SQLite persistence framework active and verified.")

def save_job_result(job_id, user_id, prompt, status, ai_response):
    """Inserts or updates a finalized background task output profile inside SQLite."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # SAFETY GUARD: Always ensure the table exists before writing data chunks to disk
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_results (
            job_id TEXT PRIMARY KEY,
            user_id TEXT,
            prompt TEXT,
            status TEXT,
            ai_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    cursor.execute("""
        INSERT OR REPLACE INTO job_results (job_id, user_id, prompt, status, ai_response)
        VALUES (?, ?, ?, ?, ?)
    """, (job_id, user_id, prompt, status, ai_response))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
