# This module isolates model calls and raw text parsing mechanics.

import re
from langchain_ollama import OllamaLLM
from config import MODEL_NAME, TEMPERATURE

class CoreLLMClient:
    """Handles deep-level calls to the locally hosted Ollama runtime instance."""
    
    def __init__(self):
        # Temp 0.0 maintains deterministic technical responses
        self.client = OllamaLLM(model=MODEL_NAME, temperature=TEMPERATURE)

    def generate(self, prompt: str) -> str:
        """Invokes raw responses while checking for memory leak paths."""
        return self.client.invoke(prompt)

    @staticmethod
    def extract_clean_code(llm_output: str) -> str:
        """Strips structural markdown decorators cleanly."""
        pattern = r"```(?:python)?\s*\n(.*?)\n\s*```"
        match = re.search(pattern, llm_output, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else llm_output.strip()
