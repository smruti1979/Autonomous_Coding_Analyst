import streamlit as st
import sqlite3
import time
from rq import Queue
from redis_config import get_redis_connection
from database import DB_FILE

# Set up page configurations
st.set_page_config(page_title="Local AI Analyst", page_icon="🤖", layout="wide")

# Initialize Redis Queue Connection
try:
    redis_conn = get_redis_connection()
    queue = Queue('sequential_analysis', connection=redis_conn)
except Exception as e:
    st.error(f"❌ Could not connect to Redis server: {e}. Please ensure redis-server is running.")

def get_all_jobs_from_db():
    """Fetches all history rows from SQLite ordered by latest creation date."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT job_id, user_id, prompt, status, ai_response, created_at 
            FROM job_results 
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

# DATABASE LOGIC: Purge Table rows smoothly
def purge_sqlite_history():
    """Deletes all records inside the job_results table permanently."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM job_results")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Database purge operation encountered an error: {e}")
        return False

# Initialize state variables
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = False
if 'show_toast' not in st.session_state:
    st.session_state.show_toast = False
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

# --- USER INTERFACE DESIGN ---

st.title("🤖 Local DeepSeek-Coder Analyst")
st.caption("Secure, sequential processing task pipeline running safely on your 8GB RAM architecture.")

# Render success toast if flag was set
if st.session_state.show_toast:
    st.toast("Database successfully cleared!", icon="🗑️")
    st.session_state.show_toast = False

# Create a layout split into two distinct visual column blocks
left_col, right_col = st.columns([1, 1.2], gap="large")

# 📥 LEFT COLUMN: Submit Deck (Never auto-refreshes, preventing typing stutter)
with left_col:
    st.header("📥 Submit Analytic Request")
    
    user_id = st.text_input("User Identifier", value="developer_1", help="Enter your name or user ID token.")
    prompt_input = st.text_area("Code Prompt Instructions", placeholder="e.g., Write a custom thread-safe singleton cache manager in Python...", height=180)
    
    if st.button("🚀 Push to Processing Queue", use_container_width=True):
        if not prompt_input.strip():
            st.warning("⚠️ Please provide prompt details before submission.")
        else:
            payload = {"user_id": user_id, "prompt": prompt_input}
            job = queue.enqueue('tasks.analyze_code', payload)
            
            st.success(f"📦 Successfully stacked in Redis cache broker!")
            st.code(f"Job ID: {job.id}", language="bash")
            st.toast("Job sent to background worker!", icon="🚀")

# 📊 RIGHT COLUMN: Real-Time Queue Track & Archive viewer
with right_col:
    
    # We wrap the entire column execution loop inside a fragment.
    # It updates the metrics and logs concurrently without touching the left side or appending duplicate pages.
    @st.fragment(run_every=3.0 if st.session_state.auto_refresh and not st.session_state.confirm_delete else None)
    def render_monitoring_deck():
        st.header("📊 Processing Monitor")
        
        # Keep track of checkbox state persistently across fragment re-runs
        st.checkbox(
            "🔄 Enable real-time monitor refresh (every 3s)", 
            key="auto_refresh"
        )
        
        try:
            active_waiting = len(queue.jobs)
        except Exception:
            active_waiting = 0
            
        st.metric(label="Queued Tasks Awaiting Execution (RAM Lock Protection)", value=active_waiting)
        
        # UI COMPONENT: Clear History Section
        st.write("---")
        
        col_refresh_status, col_clear_btn = st.columns(2)
        
        with col_clear_btn:
            def open_confirmation():
                st.session_state.confirm_delete = True

            st.button(
                "🗑️ Clear Archive History", 
                use_container_width=True, 
                type="secondary", 
                on_click=open_confirmation
            )

        # Confirmation dialogue block
        if st.session_state.confirm_delete:
            st.warning("⚠️ Are you sure? This action is permanent.")
            yes_col, no_col = st.columns(2)
            
            with yes_col:
                def execute_deletion():
                    if purge_sqlite_history():
                        st.session_state.confirm_delete = False
                        st.session_state.show_toast = True

                st.button(
                    "✅ Yes, Delete", 
                    type="primary", 
                    use_container_width=True, 
                    on_click=execute_deletion
                )
            
            with no_col:
                def cancel_deletion():
                    st.session_state.confirm_delete = False

                st.button(
                    "❌ Cancel", 
                    use_container_width=True, 
                    on_click=cancel_deletion
                )
                        
        st.write("---")
        
        st.subheader("🗄️ Unified History and Log Matrix")
        db_records = get_all_jobs_from_db()
        
        if not db_records:
            st.info("No active logs or historical entries found in SQLite instance yet.")
        else:
            for row in db_records:
                job_id, user, prompt, status, ai_response, timestamp = row
                card_label = f"🕒 {timestamp} | User: {user} | Prompt: '{prompt[:35]}...'"
                
                with st.expander(card_label):
                    st.markdown(f"**Full Token Identifier String:** `{job_id}`")
                    st.markdown(f"**User Prompt Input:** *{prompt}*")
                    
                    if status == "finished":
                        st.success("✨ Processing Complete")
                        st.markdown("### 🤖 Generated Code Output")
                        st.markdown(ai_response)
                    elif status == "failed":
                        st.error("❌ Task Processing Failed")
                        st.code(ai_response, language="python")
                    else:
                        st.warning("⏳ Job Pending in Redis Broker Stream...")

    # Execute the updated monitoring component
    render_monitoring_deck()