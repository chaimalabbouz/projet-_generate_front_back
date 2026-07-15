from langgraph.graph import StateGraph, END

from shared.state import GraphState
from shared.settings import GENERATED_PROJECT_PATH
from services.frontend.agents.seed_generator import SeedNode
from services.frontend.agents.api_client_node import FrontendApiNode
from services.frontend.agents.binding_agent import BindingAgent


def create_frontend_graph():
    graph = StateGraph(GraphState)

    seed_agent = SeedNode(project_path=GENERATED_PROJECT_PATH, rows_per_entity=5)
    api_client_agent = FrontendApiNode(project_path=GENERATED_PROJECT_PATH)
    binding_agent = BindingAgent()

    graph.add_node("seed_agent", seed_agent.run)
    graph.add_node("api_client_agent", api_client_agent.run)
    graph.add_node("binding_agent", binding_agent.run)

    graph.set_entry_point("seed_agent")
    graph.add_edge("seed_agent", "api_client_agent")
    graph.add_edge("api_client_agent", "binding_agent")
    graph.add_edge("binding_agent", END)

    return graph.compile()