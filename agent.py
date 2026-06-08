# The orchestrator. This coordinates state tracking, history storage, and the loop flow.

import uuid
from typing import Dict, Any, List
from config import MAX_RETRIES
import prompts
from LLM_engine import CoreLLMClient
from environment import ExecutionSandbox

class AutonomousAnalyst:
    """State management engine for the self-correcting analyst system loop."""
    
    def __init__(self):
        self.llm = CoreLLMClient()
        self.history: List[Dict[str, str]] = []

    def _build_history_string(self) -> str:
        """Constructs an execution timeline trace for prompt context injection."""
        return "\n".join(
            [f"Attempt {i+1}:\nCode:\n{h['code']}\nError:\n{h['error']}" 
             for i, h in enumerate(self.history)]
        )

    def run_task(self, user_goal: str, dataset_schema: str) -> Dict[str, Any]:
        """Starts the autonomous correction engine execution lifecycle."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        env = ExecutionSandbox.create_secure_env(task_id)
        
        # Prepare context injection systems
        system_base = prompts.SYSTEM_INSTRUCTIONS.format(schema_context=dataset_schema)
        active_prompt = f"{system_base}\n\nTask:\n{user_goal}"
        
        for iteration in range(MAX_RETRIES):
            print(f"🤖 [Agent Core] Processing Iteration Loop {iteration + 1}...")
            
            # Step 1: Model generation
            raw_response = self.llm.generate(active_prompt)
            clean_code = self.llm.extract_clean_code(raw_response)
            
            # Step 2: Sandbox operations
            ExecutionSandbox.resolve_dependencies(clean_code, env)
            run_metrics = ExecutionSandbox.run(clean_code, env)
            
            # Step 3: Check execution results
            if run_metrics["success"]:
                return {
                    "status": "Success",
                    "code": clean_code,
                    "output": run_metrics["stdout"],
                    "workspace": env["root"]
                }
            
            # Step 4: Logic correction fork
            print("⚠️ Logic error caught. Directing metrics data to the critic prompt framework...")
            self.history.append({"code": clean_code, "error": run_metrics["stderr"]})
            
            # Step 5: Regenerate recursive evaluation targets
            trace_log = self._build_history_string()
            active_prompt = prompts.RETRY_INSTRUCTIONS.format(history_trace=trace_log)
            
        return {"status": "Failed", "workspace": env["root"], "history": self.history}
