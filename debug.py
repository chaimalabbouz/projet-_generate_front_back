import json

with open("outputs/state_result.json", "r", encoding="utf-8") as f:
    result = json.load(f)

print("=== WORKFLOW STATE ===")
print(result["workflow_state"])

print("\n=== DEPENDENCY GRAPH ===")
print(json.dumps(result["dependency_graph"], indent=2))

print("\n=== TASK QUEUE ===")
print(json.dumps(result["task_queue"], indent=2))