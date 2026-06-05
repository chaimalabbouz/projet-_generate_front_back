import json
import re
import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import GROQ_API_KEY, PLANNER_MODEL, PROMPTS_PATH
from orchestrator.state import State

# Initialiser le LLM avec LangChain et max_tokens à 5000
llm = ChatGroq(api_key=GROQ_API_KEY, model=PLANNER_MODEL, temperature=0.1, max_tokens=5000)

def clean_thinking_tags(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()

def planner_node(state: State) -> dict:
    # 1. Charger le prompt système
    file_path = os.path.join(PROMPTS_PATH, "planner.txt")
    
    with open(file_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # 2. Préparer l'entrée utilisateur
    user_input = system_prompt.format(
        description=state["description"],
        stack=state["stack"]
    )

    try:
        # 3. Appel avec LangChain
        messages = [
            SystemMessage(content="Tu es un assistant qui répond uniquement en JSON valide."),
            HumanMessage(content=user_input)
        ]
        
        response = llm.invoke(messages)
        
        raw_content = response.content
        clean_content = clean_thinking_tags(raw_content)
        data = json.loads(clean_content)
        
        new_plan = data.get("plan", [])
        raw_specs = data.get("specs", {})

        return {
            "plan": new_plan,
            "specs": {
                "details": raw_specs
            },
            "current_step_id": None 
        }

    except Exception as e:
        print(f"Erreur Planner Agent: {e}")
        return {"erreurs": {"planner_global": str(e)}}