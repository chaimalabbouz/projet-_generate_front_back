from langgraph.graph import StateGraph, END

from shared.state import GraphState
from services.backend.agents.backend import BackendAgent
from services.backend.agents.tester import TesterAgent
from services.backend.agents.fixer import FixerAgent


# =========================
# ROUTING (repris du monolithe, inchangé)
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

    # backend + tests terminés -> fin de CE service (le front est un autre service)
    return END


def route_after_fixer(state: GraphState) -> str:
    if state.workflow_state in ["fixer_max_retries", "fixer_error"]:
        return END
    return "tester_agent"


# =========================
# GRAPH
# =========================
def create_backend_graph():
    graph = StateGraph(GraphState)

    backend_agent = BackendAgent()
    tester_agent = TesterAgent()
    fixer_agent = FixerAgent()

    graph.add_node("backend_agent", backend_agent.run)
    graph.add_node("tester_agent", tester_agent.run)
    graph.add_node("fixer_agent", fixer_agent.run)

    graph.set_entry_point("backend_agent")

    graph.add_conditional_edges(
        "backend_agent",
        route_after_backend,
        {"tester_agent": "tester_agent", END: END},
    )

    graph.add_conditional_edges(
        "tester_agent",
        route_after_tester,
        {
            "fixer_agent": "fixer_agent",
            "backend_agent": "backend_agent",
            END: END,          # ← remplace "seed_agent" du monolithe
        },
    )

    graph.add_conditional_edges(
        "fixer_agent",
        route_after_fixer,
        {"tester_agent": "tester_agent", END: END},
    )

    return graph.compile()