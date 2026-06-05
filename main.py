from orchestrator.graph import create_graph
from orchestrator.state import State
import json
from dotenv import load_dotenv

load_dotenv()

# 1. Lecture du fichier input
try:
    with open("inputs/description.txt", "r", encoding="utf-8") as f:
        contenu = f.read()
except FileNotFoundError:
    print("Erreur : Fichier inputs/description.txt introuvable.")
    exit()

# 2. Parsing (Stack vs Description)
lignes = contenu.split("\n")
stack = lignes[0].replace("Stack :", "").strip()
# On prend tout à partir de la ligne 2 en supposant que la ligne 1 est vide
description = "\n".join(lignes[2:]).strip()

# 3. Création de l'état initial (DOIT correspondre exactement à 'State')
initial_state: State = {
    "description": description,
    "stack": stack,
    
    # Structures vides mais initialisées
    "plan": [],
    "specs": {"details": {}},           # Structure définie dans Specs(TypedDict)
    "architecture": {
        "plan_fichiers": {},            # Structure définie dans Architecture(TypedDict)
        "fichiers_crees": {}
    },
    
    # État du système
    "current_step_id": None,            # Renommé depuis 'etape_courante'
    "erreurs": {},
    "tentatives": {}                    # Ajouté pour la gestion des retries
}

# 4. Lancement du graphe
print(" Lancement de l'Orchestrateur...")
graph = create_graph()

# On invoque le graphe avec l'état initial
result = graph.invoke(initial_state)

#5. Affichage du résultat
print("\n📋 Plan généré par le Planner Agent :")
print(json.dumps(result["plan"], indent=2, ensure_ascii=False))

print("\n📝 CONTENU COMPLET DES SPECS :")
# Affiche tout le dictionnaire des specs (description, input, output pour chaque ID)
print(json.dumps(result["specs"]["details"], indent=2, ensure_ascii=False))