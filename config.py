import os

# Model Settings
# Quantized model optimized for 8GB RAM footprints
MODEL_NAME = "deepseek-coder:6.7b"
TEMPERATURE = 0.0

# Execution Constraints
MAX_RETRIES = 4
TIMEOUT_SECONDS = 30

# File System Configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(BASE_DIR, "agent_workspaces")

# Dependency Safe-Mapping
PACKAGE_MAPPING = {
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn",
    "PIL": "pillow"
}
