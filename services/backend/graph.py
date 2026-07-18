from langgraph.graph import StateGraph, END

from shared.state import GraphState
from services.backend.agents.backend import BackendAgent
from services.backend.agents.tester import TesterAgent
from services.backend.agents.fixer import FixerAgent


# =========================
# NŒUD ABANDON
# =========================
def abandon_entity(state: GraphState) -> GraphState:
    """
    Une entité a épuisé ses retries : on l'abandonne proprement
    et on laisse le pipeline continuer avec les entités suivantes.
    """
    entity = None
    for task in (state.task_queue or []):
        if task.get("type") == "route" and task.get("test_status") == "failed":
            entity = task.get("entity")
            break

    if entity is None:
        state.workflow_state = "abandon_noop"
        return state

    if state.abandoned_entities is None:
        state.abandoned_entities = []
    if entity not in state.abandoned_entities:
        state.abandoned_entities.append(entity)

    # marquer toutes les tâches de cette entité comme abandonnées
    new_queue = []
    for task in state.task_queue:
        if task.get("entity") == entity:
            task = dict(task)
            task["status"] = "abandoned"
            if task.get("type") == "route":
                task["test_status"] = "abandoned"
        new_queue.append(task)
    state.task_queue = new_queue

    state.retry_count = 0          # quota neuf pour l'entité suivante
    state.workflow_state = f"entity_abandoned:{entity}"
    state.error_log = (state.error_log or "") + f"\n[ABANDON] {entity} abandonnée après {state.max_retries} tentatives"
    print(f"  ⚠ Entité abandonnée : {entity} — on continue avec les suivantes")

    return state


# =========================
# ROUTING
# =========================
def route_after_backend(state: GraphState) -> str:
    if state.workflow_state and "entity_done" in state.workflow_state:
        return "tester_agent"
    return END


def route_after_tester(state: GraphState) -> str:
    if state.workflow_state and "testing_failed" in state.workflow_state:
        return "fixer_agent"

    pending = [t for t in (state.task_queue or []) if t.get("status") == "pending"]
    if pending:
        return "backend_agent"

    return END


def route_after_fixer(state: GraphState) -> str:
    # retries épuisés ou erreur -> on abandonne CETTE entité, pas tout le pipeline
    if state.workflow_state in ["fixer_max_retries", "fixer_error"]:
        return "abandon_node"
    return "tester_agent"


def route_after_abandon(state: GraphState) -> str:
    """Après un abandon : reste-t-il des entités à générer ?"""
    pending = [t for t in (state.task_queue or []) if t.get("status") == "pending"]
    if pending:
        return "backend_agent"
    return END


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
    graph.add_node("abandon_node", abandon_entity)

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
            END: END,
        },
    )

    graph.add_conditional_edges(
        "fixer_agent",
        route_after_fixer,
        {"tester_agent": "tester_agent", "abandon_node": "abandon_node"},
    )

    graph.add_conditional_edges(
        "abandon_node",
        route_after_abandon,
        {"backend_agent": "backend_agent", END: END},
    )

    return graph.compile()