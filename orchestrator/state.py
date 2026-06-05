from typing import TypedDict, List, Dict, Any, Literal

class ElementPlan(TypedDict):
    id: str
    type: Literal["entity", "function", "endpoint", "test"]
    nom: str
    dependances: List[str]
    statut: Literal["en_attente", "en_cours", "valide", "echoue"]

class Architecture(TypedDict):
    plan_fichiers: Dict[str, str]     # ID étape -> Chemin fichier
    fichiers_crees: Dict[str, str]    # Chemin fichier -> Contenu code

class Specs(TypedDict):
    details: Dict[str, Dict[str, Any]] # ID élément -> Schéma JSON

class State(TypedDict):
    description: str #description de projet 
    stack: str  #les frawmork et langage   utilisées 
    
    plan: List[ElementPlan]
    specs: Specs
    architecture: Architecture
    
    current_step_id: str | None
    erreurs: Dict[str, str]
    
    tentatives: Dict[str, int]