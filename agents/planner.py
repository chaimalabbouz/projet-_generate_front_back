import os
import json
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import MISTRAL_API_KEY, _OpenApi_PLANNER_MODEL,PROMPTS_PATH
from orchestrator.state import GraphState




class PlannerAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=_OpenApi_PLANNER_MODEL,
            temperature=0.1,
        )

        prompt_path = os.path.join(PROMPTS_PATH, "planner.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            if not state.openapi_spec:
                raise ValueError("openapi_spec is missing from state")

            plan = self._call_llm(state.openapi_spec)

            self._validate_plan(plan)

            state.dependency_graph = plan["dependency_graph"]
            state.file_plan = plan["file_plan"]
            state.task_queue = plan["task_queue"]
            state.workflow_state = "planning_done"

        except Exception as e:
            state.workflow_state = "planning_failed"
            state.error_log = (state.error_log or "") + f"\n[PLANNER ERROR] {str(e)}"

        return state

    # =========================
    # LLM CALL
    # =========================
    def _call_llm(self, openapi_spec: dict) -> dict:
        system_prompt = self.system_prompt_template.replace(
            "{openapi_spec}",
            json.dumps(openapi_spec, indent=2)
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate the complete project plan now. Return ONLY valid JSON, no explanation, no markdown, no backticks.")
        ]

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(messages)
                raw_output = response.content
                return self._parse_json(raw_output)

            except Exception as e:
                last_error = e
                continue

        raise Exception(f"LLM call failed after 3 retries: {str(last_error)}")

    # =========================
    # SAFE JSON PARSING
    # =========================
    def _parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        raise ValueError("No valid JSON found in LLM output")

    # =========================
    # PLAN VALIDATION
    # =========================
    def _validate_plan(self, plan: dict):
        required_keys = ["dependency_graph", "file_plan", "task_queue"]
        for key in required_keys:
            if key not in plan:
                raise ValueError(f"Missing key in plan: {key}")

        if not isinstance(plan["dependency_graph"], dict):
            raise ValueError("dependency_graph must be a dictionary")

        if not isinstance(plan["file_plan"], list) or len(plan["file_plan"]) == 0:
            raise ValueError("file_plan must be a non-empty list")

        if not isinstance(plan["task_queue"], list) or len(plan["task_queue"]) == 0:
            raise ValueError("task_queue must be a non-empty list")

        for task in plan["task_queue"]:
            if "order" not in task or "file" not in task or "type" not in task:
                raise ValueError(f"Task missing required fields: {task}")