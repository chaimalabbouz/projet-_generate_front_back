import os
import json
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import MISTRAL_API_KEY, BACKEND_MODEL, PROMPTS_PATH, GENERATED_PROJECT_PATH
from orchestrator.state import GraphState


class SeedAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=BACKEND_MODEL,
            temperature=0.1,
        )
        prompt_path = os.path.join(PROMPTS_PATH, "seed.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()

    def run(self, state: GraphState) -> GraphState:
        try:
            model_files = {
                path: code
                for path, code in (state.generated_files or {}).items()
                if path.startswith("app/models/")
            }
            dependency_order = self._topological_order(state.dependency_graph or {})

            system_prompt = self.system_prompt_template.replace(
                "{model_files}", json.dumps(model_files, indent=2)
            ).replace(
                "{dependency_order}", json.dumps(dependency_order, indent=2)
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content="Generate the seed script now. Return ONLY the Python code.")
            ]

            response = self.llm.invoke(messages)
            seed_code = self._clean_code(response.content)

            self._write_file("app/seed.py", seed_code)

            if state.generated_files is None:
                state.generated_files = {}
            state.generated_files["app/seed.py"] = seed_code
            state.workflow_state = "seed_done"

        except Exception as e:
            state.workflow_state = "seed_failed"
            state.error_log = (state.error_log or "") + f"\n[SEED ERROR] {str(e)}"

        return state

    def _topological_order(self, graph: dict) -> list:
        visited, order = set(), []
        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            order.append(node)
        for entity in graph:
            visit(entity)
        return order

    def _clean_code(self, text: str) -> str:
        cleaned = re.sub(r"```(?:python)?\s*", "", text)
        return cleaned.replace("```", "").strip()

    def _write_file(self, relative_path: str, content: str):
        full_path = os.path.join(GENERATED_PROJECT_PATH, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)