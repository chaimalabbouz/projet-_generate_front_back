from langgraph.graph import StateGraph, END
from orchestrator.state import State
from agents.planner import planner_node

def create_graph():
    graph = StateGraph(State)

    graph.add_node("planner", planner_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", END)

    return graph.compile()