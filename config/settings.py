import os
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#used model
PLANNER_MODEL ="llama-3.3-70b-versatile"#cette model fait le raisonement mais on a fait un clean pour que il ne l affiche pas 
_OpenApi_PLANNER_MODEL = "mistral-medium-3.5"
BACKEND_MODEL = "codestral-latest"

####path
PROMPTS_PATH = "prompts" 
GENERATED_PROJECT_PATH = "C:/Users/binitns/Desktop/generated_project"  