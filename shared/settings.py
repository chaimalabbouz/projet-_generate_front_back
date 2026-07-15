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










# ---------------- FIGMA ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
FIGMA_API_KEY = os.getenv("FIGMA_API_KEY", "")
FIGMA_FILE_KEY = os.getenv("FIGMA_FILE_ID", "")

MODEL = "llama-3.3-70b-versatile"
CODESTRAL_MODEL = "codestral-latest"

# DATA_PATH : local = ./data  |  Docker = /workspace/data (volume)
DATA_PATH = Path(os.getenv("DATA_PATH", str(BASE_DIR / "data")))

RAW_OUTPUT_FILE          = DATA_PATH / "raw" / "figma_raw.json"
MINIMAL_OUTPUT_FILE      = DATA_PATH / "processed" / "figma_cleaned.json"
TREE_OUTPUT_FILE         = DATA_PATH / "extracted" / "tree_3levels.json"
COMPONENT_REU_OUTPUT_FILE = DATA_PATH / "extracted" / "components_reu.json"
SECTIONS_OUTPUT_FILE     = DATA_PATH / "extracted" / "sections.json"
ICONS_OUTPUT_FILE        = DATA_PATH / "extracted" / "icons.json"
INPUT_PLANNER_FILE       = DATA_PATH / "input_planner" / "payload.json"
ANALYSE_OUTPUT_FILE      = DATA_PATH / "plans" / "analyse.json"
ARCHITECTURE_FILE        = DATA_PATH / "plans" / "architecture.json"

# ---------------- PROJET GÉNÉRÉ (frontend) ----------------
OUTPUT_DIR = Path(GENERATED_PROJECT_PATH)
PROJECT_NAME = "frontend"
ASSETS_DIR     = OUTPUT_DIR / PROJECT_NAME / "src" / "assets"
COMPONENTS_DIR = OUTPUT_DIR / PROJECT_NAME / "src" / "components"
PAGES_DIR      = OUTPUT_DIR / PROJECT_NAME / "src" / "pages"   # ← corrigé (était "components")

# ---------------- MYSQL ----------------
MYSQL_HOST     = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT     = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER     = os.getenv("MYSQL_USER", "llm_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "1234")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "llm_config")