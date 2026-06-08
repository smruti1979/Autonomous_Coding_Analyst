import sys
import sqlite3
from redis_config import get_redis_connection
from rq.job import Job
from database import DB_FILE

def fetch_job_output(job_id):
    """Attempts to read from Redis real-time memory state first, falling back to permanent SQLite storage."""
    print(f"\n🔍 [Tracking] Querying profile for Job ID: {job_id}")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    
    # 1. Fallback Step: Look inside SQLite Database Archive first
    cursor.execute("SELECT user_id, prompt, status, ai_response, created_at FROM job_results WHERE job_id = ?", (job_id,))
    db_row = cursor.fetchone()
    conn.close()
    
    if db_row:
        user_id, prompt, status, ai_response, created_at = db_row
        print(f"📊 Status Source: SQLITE ARCHIVE (Saved on {created_at})")
        print("==================================================")
        print(f"🤖 DEEPSEEK-CODER OUTPUT FOR: {user_id}")
        print("==================================================")
        print(ai_response)
        print("==================================================")
        return

    # 2. Memory Step: If missing from DB, query active Redis volatile cache stack
    print("⚠️ Not found in SQLite archive. Checking volatile Redis broker...")
    redis_conn = get_redis_connection()
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.get_status()
        print(f"📊 Status Source: REDIS MEMORY ({status.upper()})")
        
        if status == 'finished':
            print("==================================================")
            print(job.result)
            print("==================================================")
        # CHANGE HERE: Add explicit logic to capture and print background worker errors
        elif status == 'failed':
            print("\n❌ [Worker Failure] The background task crashed during execution.")
            print("==================== STACK TRACE ====================")
            print(job.exc_info if job.exc_info else "No exception traceback found.")
            print("=====================================================")
        else:
            print("⏳ Task is still waiting or currently processing in the worker queue pipeline...")
    except Exception:
        print("❌ Error: That Job ID does not exist in Redis memory or SQLite archives.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("💡 Usage: python get_results.py <YOUR_JOB_ID>")
    else:
        target_id = sys.argv[1]
        fetch_job_output(target_id)
