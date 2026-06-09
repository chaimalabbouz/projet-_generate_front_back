import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PLANNER_MODEL ="llama-3.3-70b-versatile"#cette model fait le raisonement mais on a fait un clean pour que il ne l affiche pas 
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

_OpenApi_PLANNER_MODEL = "mistral-medium-3.5"

####path
PROMPTS_PATH = "prompts" 