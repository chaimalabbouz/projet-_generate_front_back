import os
import json
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage

from shared.settings import MISTRAL_API_KEY, _OpenApi_PLANNER_MODEL
from shared.state import GraphState

# prompts du SERVICE planner (services/planner/prompts/)
PROMPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


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
                return self._parse_json(response.content)   # print() supprimé
            except Exception as e:
                last_error = e
                continue

        raise Exception(f"LLM call failed after {max_retries} retries: {str(last_error)}")

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

    def _validate_openapi(self, data: dict):
        for key in ["openapi", "paths", "components"]:
            if key not in data:
                raise ValueError(f"Missing OpenAPI key: {key}")

        if "schemas" not in data.get("components", {}):
            raise ValueError("Missing components.schemas in OpenAPI")

        if not isinstance(data["paths"], dict):
            raise ValueError("paths must be a dictionary")