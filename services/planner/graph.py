from langgraph.graph import StateGraph, END

from shared.state import GraphState
from services.planner.agents.openapi_agent import OpenAPIAgent
from services.planner.agents.planner_agent import PlannerAgent
from services.planner.agents.project_initializer import initialize_project


def create_planner_graph():
    graph = StateGraph(GraphState)

    openapi_agent = OpenAPIAgent()
    planner_agent = PlannerAgent()

    graph.add_node("openapi_agent", openapi_agent.run)
    graph.add_node("planner_agent", planner_agent.run)
    graph.add_node("setup_node", initialize_project)

    graph.set_entry_point("openapi_agent")
    graph.add_edge("openapi_agent", "planner_agent")
    graph.add_edge("planner_agent", "setup_node")
    graph.add_edge("setup_node", END)

    return graph.compile()