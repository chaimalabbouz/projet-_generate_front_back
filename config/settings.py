import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PLANNER_MODEL = "qwen/qwen3-32b"#cette model fait le raisonement mais on a fait un clean pour que il ne l affiche pas 

####path
PROMPTS_PATH = "prompts" 