from langgraph.graph import StateGraph, END

from shared.state import GraphState
from services.design.agents.figma_generator import FigmaGeneratorAgent


def create_design_graph():
    """
    Un seul nœud : le FigmaGeneratorAgent orchestre déjà tout le
    pipeline figma en interne (extraction -> analyse -> génération).
    """
    graph = StateGraph(GraphState)

    figma_agent = FigmaGeneratorAgent()
    graph.add_node("figma_generator", figma_agent.run)

    graph.set_entry_point("figma_generator")
    graph.add_edge("figma_generator", END)

    return graph.compile()