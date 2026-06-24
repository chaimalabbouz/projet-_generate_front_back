import os
from dotenv import load_dotenv
from pathlib import Path



load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FIGMA_FILE_KEY = os.getenv("GROQ_API_KEY")
FIGMA_API_KEY = os.getenv("FIGMA_API_KEY")

#used model
PLANNER_MODEL ="llama-3.3-70b-versatile"#cette model fait le raisonement mais on a fait un clean pour que il ne l affiche pas 
_OpenApi_PLANNER_MODEL = "mistral-medium-3.5"
BACKEND_MODEL = "codestral-latest"
TESTER_MODEL = "codestral-latest"

####path
PROMPTS_PATH = "prompts" 
GENERATED_PROJECT_PATH = "C:/Users/binitns/Desktop/generated_project" 



#####################la partie de figma services
BASE_DIR = Path(__file__).resolve().parent.parent
FIGMA_API_KEY = os.getenv("FIGMA_API_KEY", "")
FIGMA_FILE_KEY = os.getenv("FIGMA_FILE_ID", "")


MODEL ="llama-3.3-70b-versatile"
CODESTRAL_MODEL = "codestral-latest"


# Inputs existants
RAW_OUTPUT_FILE = BASE_DIR / "data" / "raw" / "figma_raw.json"
MINIMAL_OUTPUT_FILE = BASE_DIR / "data" / "processed" / "figma_cleaned.json"

# Data isolée du sous-projet
#DATA2_DIR = BASE_DIR / "data2"

TREE_OUTPUT_FILE = BASE_DIR / "data" / "extracted" / "tree_3levels.json"
#REUSABLE_OUTPUT_FILE = DATA2_DIR / "extracted" / "reusable_components.json"
#voici la nouvelle
COMPONENT_REU_OUTPUT_FILE = BASE_DIR / "data"  / "extracted" / "components_reu.json"
SECTIONS_OUTPUT_FILE = BASE_DIR / "data"  / "extracted" / "sections.json"

INPUT_PLANNER_FILE = BASE_DIR / "data"  / "input_planner" / "payload.json"

ANALYSE_OUTPUT_FILE = BASE_DIR / "data"  / "plans" / "analyse.json"
ARCHITECTURE_FILE = BASE_DIR / "data"  / "plans" / "architecture.json"
ICONS_OUTPUT_FILE = BASE_DIR / "data" / "extracted" / "icons.json"

######chemin de projet generé :
OUTPUT_DIR = Path(GENERATED_PROJECT_PATH)
PROJECT_NAME = "frontend"
ASSETS_DIR = OUTPUT_DIR / PROJECT_NAME / "src" / "assets"
COMPONENTS_DIR = OUTPUT_DIR / PROJECT_NAME / "src" / "components"
PAGES_DIR = OUTPUT_DIR / PROJECT_NAME / "src" / "components"














