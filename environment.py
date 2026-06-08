# This component completely handles OS-level sandbox tasks, dependencies, 
# and code execution safely away from the LLM logic.

import os
import sys
import venv
import subprocess
import re
from typing import Dict, Any, List
from config import WORKSPACE_DIR, PACKAGE_MAPPING, TIMEOUT_SECONDS

class ExecutionSandbox:
    """Manages virtual environments and handles safe command run lines."""
    
    @staticmethod
    def create_secure_env(task_id: str) -> Dict[str, str]:
        """Sets up a brand new python virtual environment folder structure."""
        root_path = os.path.join(WORKSPACE_DIR, task_id)
        os.makedirs(root_path, exist_ok=True)
        
        venv_dir = os.path.join(root_path, "venv")
        venv.create(venv_dir, with_pip=True)
        
        if sys.platform == "win32":
            python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
            pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
        else:
            python_exe = os.path.join(venv_dir, "bin", "python")
            pip_exe = os.path.join(venv_dir, "bin", "pip")
            
        return {"root": root_path, "python": python_exe, "pip": pip_exe}

    @staticmethod
    def resolve_dependencies(code: str, env: Dict[str, str]) -> None:
        """Parses active script import strings and runs auto-pip hooks."""
        found_modules = re.findall(r"^(?:import|from)\s+([a-zA-Z0-9_]+)", code, re.MULTILINE)
        
        for mod in found_modules:
            package = PACKAGE_MAPPING.get(mod, mod)
            if package in sys.builtin_module_names or package in ["os", "sys", "re"]: 
                continue
            try:
                subprocess.run([env["pip"], "install", package], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                pass 

    @staticmethod
    def run(code: str, env: Dict[str, str]) -> Dict[str, Any]:
        """Executes targeted scripts within strict timeout constraints."""
        script_path = os.path.join(env["root"], "analyst_script.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        try:
            res = subprocess.run(
                [env["python"], script_path],
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=env["root"]
            )
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Execution timed out (possible infinite loop)."}
