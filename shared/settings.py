import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# ---------------- INPUT ----------------
INPUT_FILE = os.getenv("INPUT_FILE", "inputs/description.txt")

# ---------------- API KEYS ----------------
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FIGMA_API_KEY = os.getenv("FIGMA_API_KEY", "")
FIGMA_FILE_KEY = os.getenv("FIGMA_FILE_ID", "")

# ---------------- MODELS ----------------
_OpenApi_PLANNER_MODEL = "mistral-medium-3.5"
BACKEND_MODEL = "codestral-latest"
TESTER_MODEL = "codestral-latest"
BINDING_MODEL = "devstral-latest"
FIXER_MODEL = "devstral-latest"

# ---------------- PATHS ----------------
# Chemin du projet généré.
#   - en local  : ton dossier Desktop (défaut)
#   - en Docker : /workspace/generated (injecté par docker-compose)
GENERATED_PROJECT_PATH = os.getenv(
    "GENERATED_PROJECT_PATH",
    "C:/Users/binitns/Desktop/generated_project",
)

# Dossier des fichiers de debug (debug_plan.json, etc.)
DEBUG_PATH = os.getenv("DEBUG_PATH", os.path.join(GENERATED_PROJECT_PATH, "_debug"))

# ---------------- REDIS / CELERY ----------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")