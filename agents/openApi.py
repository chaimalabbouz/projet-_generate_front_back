import os
import json
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import MISTRAL_API_KEY, _OpenApi_PLANNER_MODEL, PROMPTS_PATH
from orchestrator.state import GraphState


class OpenAPIAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=_OpenApi_PLANNER_MODEL,
            temperature=0.2,
             
        )

        prompt_path = os.path.join(PROMPTS_PATH, "openApi.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            openapi_json = self._call_llm(state.user_input)
            self._validate_openapi(openapi_json)
            state.openapi_spec = openapi_json
            state.workflow_state = "openapi_done"

        except Exception as e:
            state.openapi_spec = None
            state.workflow_state = "openapi_failed"
            state.error_log = (state.error_log or "") + f"\n[OpenAPI ERROR] {str(e)}"

        return state

    # =========================
    # LLM CALL
    # =========================
    def _call_llm(self, user_input: str) -> dict:
        system_prompt = self.system_prompt_template.replace("{user_input}", user_input)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate the OpenAPI specification now. Return ONLY valid JSON, no explanation, no markdown, no backticks.")
        ]

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(messages)
                raw_output = response.content
                print(raw_output)  # TEMPORAIRE pour debugger
                return self._parse_json(raw_output)

            except Exception as e:
                last_error = e
                continue

        raise Exception(f"LLM call failed after {max_retries} retries: {str(last_error)}")

    # =========================
    # SAFE JSON PARSING
    # =========================
    def _parse_json(self, text: str) -> dict:
        # essaye directement
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # enleve les backticks markdown ```json ... ```
        cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # extrait le premier bloc JSON valide
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        raise ValueError("No valid JSON found in LLM output")

    # =========================
    # BASIC OPENAPI VALIDATION
    # =========================
    def _validate_openapi(self, data: dict):
        required_keys = ["openapi", "paths", "components"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing OpenAPI key: {key}")

        if "schemas" not in data.get("components", {}):
            raise ValueError("Missing components.schemas in OpenAPI")

        if not isinstance(data["paths"], dict):
            raise ValueError("paths must be a dictionary")