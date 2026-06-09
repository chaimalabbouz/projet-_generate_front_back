from langgraph.graph import StateGraph, END
from orchestrator.state import GraphState
from agents.openApi import OpenAPIAgent
from agents.planner import PlannerAgent

def create_graph():
    graph = StateGraph(GraphState)

    openapi_agent = OpenAPIAgent()
    planner_agent = PlannerAgent()

    graph.add_node("openapi_agent", openapi_agent.run)
    graph.add_node("planner_agent", planner_agent.run)

    graph.set_entry_point("openapi_agent")
    graph.add_edge("openapi_agent", "planner_agent")
    graph.add_edge("planner_agent", END)

    return graph.compile()




