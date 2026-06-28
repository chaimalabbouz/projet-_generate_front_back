from langgraph.graph import StateGraph, END
from orchestrator.state import GraphState
from agents.openApi import OpenAPIAgent
from agents.planner import PlannerAgent
from agents.backend import BackendAgent
from agents.tester import TesterAgent
from agents.fixer import FixerAgent
from setup.project_initializer import initialize_project
# --- partie post-backend (désactivée pour l'instant, NE PAS supprimer) ---
# from agents.frontend import FrontendAgent
# from agents.seed import SeedAgent
# from agents.figma_generator import FigmaGeneratorAgent

# =========================
# ROUTING FUNCTIONS
# =========================
def route_after_backend(state: GraphState) -> str:
    if state.workflow_state and "entity_done" in state.workflow_state:
        return "tester_agent"
    return END


def route_after_tester(state: GraphState) -> str:
    if state.workflow_state and "failed" in state.workflow_state:
        return "fixer_agent"
    pending = [t for t in state.task_queue if t.get("status") == "pending"]
    if pending:
        return "backend_agent"
    # --- avant : on enchaînait sur le seed_agent ---
    # return "seed_agent"
    return END


def route_after_fixer(state: GraphState) -> str:
    if state.workflow_state in ["fixer_max_retries", "fixer_error"]:
        return END
    return "tester_agent"


# =========================
# GRAPH
# =========================
def create_graph():
    graph = StateGraph(GraphState)

    # agents
    openapi_agent = OpenAPIAgent()
    planner_agent = PlannerAgent()
    backend_agent = BackendAgent()
    tester_agent = TesterAgent()
    fixer_agent = FixerAgent()
    # --- agents post-backend (désactivés, NE PAS supprimer) ---
    # frontend_agent = FrontendAgent()
    # figma_generator_agent = FigmaGeneratorAgent()
    # seed_agent = SeedAgent()

    # nodes
    graph.add_node("openapi_agent", openapi_agent.run)
    graph.add_node("planner_agent", planner_agent.run)
    graph.add_node("setup_node", initialize_project)
    graph.add_node("backend_agent", backend_agent.run)
    graph.add_node("tester_agent", tester_agent.run)
    graph.add_node("fixer_agent", fixer_agent.run)
    # --- nodes post-backend (désactivés, NE PAS supprimer) ---
    # graph.add_node("frontend_agent", frontend_agent.run)
    # graph.add_node("figma_generator_agent", figma_generator_agent.run)
    # graph.add_node("seed_agent", seed_agent.run)

    # edges
    graph.set_entry_point("openapi_agent")
    graph.add_edge("openapi_agent", "planner_agent")

    # setup_node réactivé : crée la structure de dossiers / Base.metadata.create_all
    # avant que le backend_agent ne commence à générer les fichiers
    graph.add_edge("planner_agent", "setup_node")
    graph.add_edge("setup_node", "backend_agent")

    graph.add_conditional_edges(
        "backend_agent",
        route_after_backend,
        {
            "tester_agent": "tester_agent",
            END: END
        }
    )

    graph.add_conditional_edges(
        "tester_agent",
        route_after_tester,
        {
            "fixer_agent": "fixer_agent",
            "backend_agent": "backend_agent",
            # --- avant : "seed_agent": "seed_agent", ---
            END: END
        }
    )

    graph.add_conditional_edges(
        "fixer_agent",
        route_after_fixer,
        {
            "tester_agent": "tester_agent",
            END: END
        }
    )

    # --- partie post-backend (désactivée, NE PAS supprimer) ---
    # graph.add_edge("seed_agent", "figma_generator_agent")
    # graph.add_edge("figma_generator_agent", "frontend_agent")
    # graph.add_edge("frontend_agent", END)

    return graph.compile()