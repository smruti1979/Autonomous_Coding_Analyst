import time
from rq import Queue
from redis_config import get_redis_connection

# 1. Get the unified connection
redis_conn = get_redis_connection()

# 2. Pass the connection explicitly to the queue initialization object
queue = Queue('sequential_analysis', connection=redis_conn)

def send_task_to_queue(prompt_data):
    # Enqueue the background task
    job = queue.enqueue('tasks.analyze_code', prompt_data)
    print(f"🚀 Sent job to Redis queue! Job ID: {job.id}")

if __name__ == '__main__':
    print("🔥 Simulating multiple incoming user requests...")
    
    # Mocking 3 unique user prompts fired rapidly
    sample_prompts = [
        {"user_id": "user_1", "prompt": "Write a quicksort algorithm in Python"},
        {"user_id": "user_2", "prompt": "Optimize this SQL query interface"},
        {"user_id": "user_3", "prompt": "Fix the memory leak in this C++ loop"}
    ]
    
    for idx, data in enumerate(sample_prompts, start=1):
        print(f"\n[Trigger] User {idx} hits the submit button...")
        send_task_to_queue(data)
        
    print("\n✅ All jobs successfully stacked in Redis! Check Terminal 2 to watch them process.")
