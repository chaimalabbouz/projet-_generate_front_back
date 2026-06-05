from typing import List, Dict, Optional
from state import State, ElementPlan

class Orchestrator:

    def valider_plan(self, plan: List[ElementPlan]) -> Optional[str]:
        # Récupération de tous les IDs pour vérifier les dépendances
        ids = [e["id"] for e in plan]
        
        for element in plan:
            # Vérification de la présence des champs obligatoires
            required_fields = ["id", "type", "nom", "dependances", "statut"]
            for field in required_fields:
                if field not in element:
                    return f"L'élément {element.get('id', 'INCONNU')} n'a pas de champ '{field}'"
            
            # Vérification des types autorisés
            valid_types = ["entity", "function", "endpoint", "test"]
            if element["type"] not in valid_types:
                return f"L'élément {element['id']} a un type invalide : {element['type']}"

            # Vérification que les dépendances existent bien dans le plan
            for dep_id in element["dependances"]:
                if dep_id not in ids:
                    return f"L'élément {element['id']} dépend de '{dep_id}' qui n'existe pas dans le plan."
        
        return None

    def can_retry(self, key: str, state: State) -> bool:
        # CORRECTION : On vérifie le compteur à la racine du State (champ 'tentatives')
        # et non plus dans state["erreurs"]["tentatives"]
        tentatives_actuelles = state["tentatives"].get(key, 0)
        return tentatives_actuelles < 3

    def incrementer_tentative(self, key: str, rapport: str, state: State) -> State:
        # CORRECTION : On met à jour le compteur principal 'tentatives'
        state["tentatives"][key] = state["tentatives"].get(key, 0) + 1
        
        # On met à jour le message d'erreur séparément
        state["erreurs"][key] = rapport
        
        return state