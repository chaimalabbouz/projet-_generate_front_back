
import json
import os
from orchestrator.graph import create_graph
from orchestrator.state import GraphState

def main():
    graph = create_graph()

    with open("inputs/description.txt", "r", encoding="utf-8") as f:
        user_input = f.read()

    initial_state = GraphState(user_input=user_input)

    result = graph.invoke(initial_state)

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/state_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Pipeline terminée. Résultat sauvegardé dans outputs/state_result.json")

if __name__ == "__main__":
    main()
   
