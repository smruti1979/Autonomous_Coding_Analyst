from typing import Dict, Any
from agent import AutonomousAnalyst

def process_analysis_task(user_goal: str, dataset_metadata: str) -> Dict[str, Any]:
    """
    Core entry execution block. 
    This function is executed inside the background worker process.
    """
    analyst_agent = AutonomousAnalyst()
    
    print(f"🚀 Starting task: {user_goal[:30]}...")
    result = analyst_agent.run_task(user_goal=user_goal, dataset_schema=dataset_metadata)
    
    print(f"🏁 Task complete with status: {result['status']}")
    return result
