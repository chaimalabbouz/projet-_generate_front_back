"""
Graphe de TEST réduit.
But : exécuter la pipeline UNIQUEMENT jusqu'à la génération backend,
pour vérifier que models/category.py et models/product.py sortent
sans 'description' ni 'relationship'.

Flux : openapi_agent -> planner_agent -> setup_node -> backend_agent -> END

Le backend_agent boucle déjà entité par entité tant qu'il reste des tâches
'pending' avec une entité. On reboucle donc backend -> backend jusqu'à ce
qu'il n'y ait plus rien à générer, puis on s'arrête (END).
On NE branche PAS tester / fixer / seed / figma / frontend.
"""

from langgraph.graph import StateGraph, END
from orchestrator.state import GraphState
from agents.openApi import OpenAPIAgent
from agents.planner import PlannerAgent
from agents.backend import BackendAgent
from setup.project_initializer import initialize_project


# =========================
# ROUTING
# =========================
def route_after_backend(state: GraphState) -> str:
    """
    Tant qu'il reste des tâches 'pending' (modèles/schemas/services/routes
    pas encore générés), on relance le backend. Sinon on termine.
    On ignore la tâche 'main' pour ce test (optionnel) : si tu veux générer
    main.py aussi, garde la condition telle quelle.
    """
    pending = [
        t for t in (state.task_queue or [])
        if t.get("status") == "pending"
    ]
    if pending:
        return "backend_agent"
    return END


# =========================
# GRAPH
# =========================
def create_test_graph():
    graph = StateGraph(GraphState)

    # agents
    openapi_agent = OpenAPIAgent()
    planner_agent = PlannerAgent()
    backend_agent = BackendAgent()

    # nodes
    graph.add_node("openapi_agent", openapi_agent.run)
    graph.add_node("planner_agent", planner_agent.run)
    graph.add_node("setup_node", initialize_project)
    graph.add_node("backend_agent", backend_agent.run)

    # edges
    graph.set_entry_point("openapi_agent")
    graph.add_edge("openapi_agent", "planner_agent")
    graph.add_edge("planner_agent", "setup_node")
    graph.add_edge("setup_node", "backend_agent")

    # boucle backend jusqu'à épuisement des tâches pending, puis END
    graph.add_conditional_edges(
        "backend_agent",
        route_after_backend,
        {
            "backend_agent": "backend_agent",
            END: END,
        },
    )

    return graph.compile()


# =========================
# RUN
# =========================
if __name__ == "__main__":
    user_input = """STACK: Python / FastAPI systems

PROJECT: E-Commerce Product Catalog API

DESCRIPTION:
An API for managing and browsing an online product catalog. Users can view products, browse products by category, search products by name or category, and access detailed product information.

FEATURES:

CATEGORIES:
* view all categories
* view products by category

PRODUCTS:
* view all products
* search products by name
* search products by category
* view product details

DATA MODELS:

Category:
* name: string

Product:
* name: string
* description: string
* rating: float
* price: float
* image_url: string
* category: Category
* manufacturer: string
* product_dimensions: string
* item_model_number: string
* date_first_available: date
* product_number: string
* country_of_origin: string
* best_sellers_rank: string
"""

    initial_state = GraphState(user_input=user_input)

    app = create_test_graph()
    final_state = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("BACKEND GENERATION TERMINÉE")
    print("=" * 60)

    # langgraph renvoie un dict
    gen = final_state.get("generated_files", {}) or {}

    print("\nFichiers générés :")
    for path in sorted(gen.keys()):
        print(f"  - {path}")

    # affiche directement le modèle Category pour vérification immédiate
    cat_path = "app/models/category.py"
    if cat_path in gen:
        print("\n" + "-" * 60)
        print(f"CONTENU DE {cat_path} :")
        print("-" * 60)
        print(gen[cat_path])

    # vérification automatique des 3 points clés
    print("\n" + "-" * 60)
    print("VÉRIFICATION AUTOMATIQUE (Category)")
    print("-" * 60)
    cat_code = gen.get(cat_path, "")
    checks = {
        "pas de 'description'": "description" not in cat_code,
        "pas de 'relationship('": "relationship(" not in cat_code,
        "pas de 'back_populates'": "back_populates" not in cat_code,
    }
    for label, ok in checks.items():
        print(f"  {'✓' if ok else '✗'} {label}")

    if all(checks.values()):
        print("\n✅ ÉTAPE 1 VALIDÉE : le backend ne pollue plus Category.")
    else:
        print("\n❌ Le backend produit encore des éléments hors spec. Voir ci-dessus.")

    # affiche aussi un éventuel warning de validation laissé dans error_log
    err = final_state.get("error_log")
    if err and "[BACKEND VALIDATION]" in err:
        print("\n⚠ Avertissements de validation détectés dans error_log :")
        for line in err.splitlines():
            if "[BACKEND VALIDATION]" in line:
                print("  " + line.strip())