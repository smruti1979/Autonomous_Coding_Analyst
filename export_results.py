import sys
import os
import sqlite3
from database import DB_FILE

def export_job_to_file(job_id):
    """Fetches the AI output from SQLite and saves it as a clean local script file."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, ai_response FROM job_results WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"❌ Error: No archived data found for Job ID: {job_id}")
        return
        
    user_id, ai_response = row
    
    # Define a clean file name using the user id and job footprint
    filename = f"output_{user_id}_{job_id[:8]}.md"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(ai_response)
        print(f"💾 [Export Success] File written cleanly to disk!")
        print(f"📂 Location: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"❌ Failed to write file: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("💡 Usage: python export_results.py <YOUR_JOB_ID>")
    else:
        export_job_to_file(sys.argv[1])
