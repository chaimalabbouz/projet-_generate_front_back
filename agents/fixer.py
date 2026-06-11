import os
import json
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from config.settings import MISTRAL_API_KEY, PROMPTS_PATH, GENERATED_PROJECT_PATH
from orchestrator.state import GraphState

FIXER_MODEL = "devstral-latest"


# =========================
# TOOLS
# =========================
@tool
def read_file(path: str) -> str:
    """Read a file from the generated project directory."""
    full_path = os.path.join(GENERATED_PROJECT_PATH, path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"File not found: {path}"


@tool
def write_file(path: str, content: str) -> str:
    """Write fixed code to a file in the generated project directory."""
    full_path = os.path.join(GENERATED_PROJECT_PATH, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written successfully: {path}"


@tool
def list_entity_files(entity: str) -> str:
    """List all files related to an entity."""
    entity_lower = entity.lower()
    files = [
        f"app/models/{entity_lower}.py",
        f"app/schemas/{entity_lower}.py",
        f"app/services/{entity_lower}.py",
        f"app/routes/{entity_lower}.py",
        f"tests/test_{entity_lower}.py",
    ]
    result = []
    for f in files:
        full_path = os.path.join(GENERATED_PROJECT_PATH, f)
        exists = "EXISTS" if os.path.exists(full_path) else "NOT FOUND"
        result.append(f"{f} → {exists}")
    return "\n".join(result)


class FixerAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=FIXER_MODEL,
            temperature=0.1,
        )

        prompt_path = os.path.join(PROMPTS_PATH, "fixer.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

        self.tools = [read_file, write_file, list_entity_files]

        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
        )

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            current_entity = self._get_failed_entity(state.task_queue)

            if current_entity is None:
                state.workflow_state = "fixer_done"
                return state

            if state.retry_count >= state.max_retries:
                state.workflow_state = "fixer_max_retries"
                state.error_log = (state.error_log or "") + f"\n[FIXER] Max retries reached for {current_entity}"
                return state

            error_output = self._get_error_output(current_entity, state.test_results)

            prompt = f"""{self.system_prompt}

ENTITY TO FIX: {current_entity}

ERROR OUTPUT:
{error_output}

Use your tools to:
1. List the entity files with list_entity_files("{current_entity}")
2. Read each file with read_file to understand the code
3. Analyze the error and identify what needs to be fixed
4. Write the fixed files with write_file
"""

            result = self.agent.invoke({
                "messages": [{"role": "user", "content": prompt}]
            })

            for message in result["messages"]:
                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tool_call in message.tool_calls:
                        if tool_call["name"] == "write_file":
                            path = tool_call["args"]["path"]
                            content = tool_call["args"]["content"]
                            state.generated_files[path] = content
                            print(f"  🔧 Fixed: {path}")

            new_task_queue = []
            for task in state.task_queue:
                if task.get("entity") == current_entity and task.get("type") == "route":
                    task = dict(task)
                    task["test_status"] = "pending"
                new_task_queue.append(task)
            state.task_queue = new_task_queue

            state.retry_count += 1
            state.workflow_state = f"fixer_done:{current_entity}"

        except Exception as e:
            state.workflow_state = "fixer_error"
            state.error_log = (state.error_log or "") + f"\n[FIXER ERROR] {str(e)}"

        return state

    # =========================
    # GET FAILED ENTITY
    # =========================
    def _get_failed_entity(self, task_queue: list) -> str:
        for task in task_queue:
            if task.get("type") == "route" and task.get("test_status") == "failed":
                return task.get("entity")
        return None

    # =========================
    # GET ERROR OUTPUT
    # =========================
    def _get_error_output(self, entity: str, test_results: dict) -> str:
        if test_results and entity in test_results:
            return test_results[entity].get("output", "No error output available")
        return "No error output available"