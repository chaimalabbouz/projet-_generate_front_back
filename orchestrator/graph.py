from langgraph.graph import StateGraph, END
from orchestrator.state import GraphState
from agents.openApi import OpenAPIAgent
from agents.planner import PlannerAgent
from agents.backend import BackendAgent
from setup.project_initializer import initialize_project


def create_graph():
    graph = StateGraph(GraphState)

    #agents
    openapi_agent = OpenAPIAgent()
    planner_agent = PlannerAgent()
    backend_agent = BackendAgent()

    #node
    graph.add_node("openapi_agent", openapi_agent.run)
    graph.add_node("planner_agent", planner_agent.run)
    graph.add_node("setup_node", initialize_project)
    graph.add_node("backend_agent", backend_agent.run)

    #edge
    graph.set_entry_point("openapi_agent")
    graph.add_edge("openapi_agent", "planner_agent")
    #graph.add_edge("planner_agent", "setup_node")
    #graph.add_edge("setup_node", END)
    graph.add_edge("planner_agent","backend_agent")
    graph.add_edge("backend_agent", END)


    return graph.compile()




