# Actual background worker script. Running it sets your system up to listen for requests.

import sys
# CHANGE HERE: Import SimpleWorker instead of Worker
from rq import SimpleWorker, Queue
from redis_config import get_redis_connection

def start_worker():
    """Spawns a single worker listening exclusively to a sequential queue."""
    # Obtain the direct connection object
    redis_conn = get_redis_connection()
    
    # Listening to exactly one queue named 'sequential_analysis'
    listen_queue = ['sequential_analysis']
    
    # CHANGE HERE: Use SimpleWorker to prevent os.fork() errors on Windows
    worker = SimpleWorker(listen_queue, connection=redis_conn)
    
    print("🤖 [Worker System] Active. Waiting sequentially for incoming tasks...")
    print("🛑 Memory protection mode: Active (Windows Single-Process Mode).")
    worker.work()

if __name__ == '__main__':
    # Fix python path environment injection hooks if running locally
    if "." not in sys.path:
        sys.path.append(".")
    start_worker()
