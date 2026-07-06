"""
Lance UNIQUEMENT la partie backend de la pipeline
(openapi -> planner -> setup -> backend -> tester -> fixer),
sans seed_agent / api_client_agent / binding_agent.

Tout est dans ce seul fichier : le graph + le script d'execution.

Usage:
    python test.py
"""

from langgraph.graph import StateGraph, END
from orchestrator.state import GraphState
from agents.openApi import OpenAPIAgent
from agents.planner import PlannerAgent
from agents.backend import BackendAgent
from agents.tester import TesterAgent
from agents.fixer import FixerAgent
from setup.project_initializer import initialize_project

# chemin vers le spec simplifie (3 entites simples, sans date, sans FK)
INPUT_FILE = "inputs/description.txt"


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
    pending = [t for t in (state.task_queue or []) if t.get("status") == "pending"]
    if pending:
        return "backend_agent"
    return END


def route_after_fixer(state: GraphState) -> str:
    if state.workflow_state in ["fixer_max_retries", "fixer_error"]:
        return END
    return "tester_agent"


# =========================
# GRAPH (backend only)
# =========================
def create_graph_backend_only():
    graph = StateGraph(GraphState)

    openapi_agent = OpenAPIAgent()
    planner_agent = PlannerAgent()
    backend_agent = BackendAgent()
    tester_agent = TesterAgent()
    fixer_agent = FixerAgent()

    graph.add_node("openapi_agent", openapi_agent.run)
    graph.add_node("planner_agent", planner_agent.run)
    graph.add_node("setup_node", initialize_project)
    graph.add_node("backend_agent", backend_agent.run)
    graph.add_node("tester_agent", tester_agent.run)
    graph.add_node("fixer_agent", fixer_agent.run)

    graph.set_entry_point("openapi_agent")
    graph.add_edge("openapi_agent", "planner_agent")
    graph.add_edge("planner_agent", "setup_node")
    graph.add_edge("setup_node", "backend_agent")

    graph.add_conditional_edges(
        "backend_agent",
        route_after_backend,
        {"tester_agent": "tester_agent", END: END}
    )

    graph.add_conditional_edges(
        "tester_agent",
        route_after_tester,
        {"fixer_agent": "fixer_agent", "backend_agent": "backend_agent", END: END}
    )

    graph.add_conditional_edges(
        "fixer_agent",
        route_after_fixer,
        {"tester_agent": "tester_agent", END: END}
    )

    return graph.compile()


# =========================
# MAIN
# =========================
def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        user_input = f.read()

    initial_state = GraphState(
        user_input=user_input,
        stack="Python / FastAPI",
    )

    graph = create_graph_backend_only()
    final_state = graph.invoke(initial_state)

    print("\n\n========== RESULTAT FINAL ==========")
    print("workflow_state:", final_state.get("workflow_state") if isinstance(final_state, dict) else final_state.workflow_state)

    test_results = final_state.get("test_results") if isinstance(final_state, dict) else final_state.test_results
    if test_results:
        print("\n--- test_results ---")
        for entity, result in test_results.items():
            print(f"  {entity}: {result.get('status')}")

    error_log = final_state.get("error_log") if isinstance(final_state, dict) else final_state.error_log
    if error_log:
        print("\n--- error_log ---")
        print(error_log)


if __name__ == "__main__":
    main()