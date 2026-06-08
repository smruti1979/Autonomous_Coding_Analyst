import os
import time
import ollama
from rq import get_current_job  # Added to grab active execution metadata
from database import save_job_result

OLLAMA_MODEL = "deepseek-coder:6.7b"

def analyze_code(prompt_data):
    """
    Worker task that fetches responses from Ollama and permanently 
    commits the transaction into SQLite before releasing worker memory footprint.
    """
    # Safely pull current RQ job tracking footprint details
    current_job = get_current_job()
    job_id = current_job.id if current_job else "manual_execution"
    
    user = prompt_data.get("user_id", "Unknown User")
    prompt = prompt_data.get("prompt", "")
    
    print(f"\n⚡ [Processing] Route task to DeepSeek-Coder:6.7b for {user} (Job: {job_id})...")
    
    start_time = time.time()
    
    try:
        system_instructions = (
            "You are an expert software engineering assistant. "
            "Provide clean, efficient, and well-commented code responses."
        )
        
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt}
            ],
            options={"temperature": 0.2, "num_ctx": 4096}
        )
        
        ai_response_text = response['message']['content']
        duration = time.time() - start_time
        print(f"✨ [Completed] Generated AI output in {duration:.2f} seconds.")
        
        # PERSISTENCE HOOK: Write straight to the local SQLite DB disk asset permanently
        save_job_result(
            job_id=job_id,
            user_id=user,
            prompt=prompt,
            status="finished",
            ai_response=ai_response_text
        )
        print(f"💾 [Storage Hook] Job {job_id} successfully persisted to SQLite archive.")
        
        return ai_response_text

    except Exception as e:
        print(f"❌ [System Error] Task failed: {e}")
        # Log the failure state to database as well for debugging metrics tracking
        save_job_result(
            job_id=job_id,
            user_id=user,
            prompt=prompt,
            status="failed",
            ai_response=str(e)
        )
        raise e
