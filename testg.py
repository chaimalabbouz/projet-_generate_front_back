from orchestrator.graph import create_graph  # adapte l'import à ton projet

graph = create_graph()

png_data = graph.get_graph().draw_mermaid_png()
with open("graphhh.png", "wb") as f:
    f.write(png_data)

print("Image sauvée : graphhh.png")