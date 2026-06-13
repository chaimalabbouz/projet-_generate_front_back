import os
import json
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import MISTRAL_API_KEY, PROMPTS_PATH, GENERATED_PROJECT_PATH
from orchestrator.state import GraphState

FRONTEND_MODEL = "mistral-medium-3.5"
FRONTEND_PATH = os.path.join(GENERATED_PROJECT_PATH, "frontend")


class FrontendAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=FRONTEND_MODEL,
            temperature=0.1,
        )

        prompt_path = os.path.join(PROMPTS_PATH, "frontend.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            if not state.openapi_spec:
                raise ValueError("openapi_spec is missing from state")

            endpoints = self._extract_endpoints(state.openapi_spec)

            api_service_code = self._generate_api_service(endpoints)
            self._write_file("src/services/api.ts", api_service_code)
            state.frontend_api_service = api_service_code
            print("  ✓ Generated: src/services/api.ts")

            pages_dir = os.path.join(FRONTEND_PATH, "src", "pages")
            if not os.path.exists(pages_dir):
                raise ValueError(f"Pages directory not found: {pages_dir}")

            if state.frontend_pages is None:
                state.frontend_pages = {}

            for filename in os.listdir(pages_dir):
                if not filename.endswith(".tsx") and not filename.endswith(".ts"):
                    continue

                page_path = os.path.join(pages_dir, filename)
                with open(page_path, "r", encoding="utf-8") as f:
                    page_code = f.read()

                modified_code = self._call_llm(filename, page_code, endpoints)

                self._write_file(f"src/pages/{filename}", modified_code)
                state.frontend_pages[filename] = modified_code
                print(f"  ✓ Modified: src/pages/{filename}")

            state.workflow_state = "frontend_done"

        except Exception as e:
            state.workflow_state = "frontend_failed"
            state.error_log = (state.error_log or "") + f"\n[FRONTEND ERROR] {str(e)}"

        return state

    # =========================
    # EXTRACT ENDPOINTS
    # =========================
    def _extract_endpoints(self, openapi_spec: dict) -> list:
        endpoints = []
        paths = openapi_spec.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    endpoints.append({
                        "method": method.upper(),
                        "path": path,
                        "summary": details.get("summary", ""),
                        "operationId": details.get("operationId", ""),
                        "requestBody": details.get("requestBody", None),
                        "responses": list(details.get("responses", {}).keys()),
                    })

        return endpoints

    # =========================
    # GENERATE API SERVICE
    # =========================
    def _generate_api_service(self, endpoints: list) -> str:
        functions = []
        functions.append('import API_BASE_URL from "../config/api";\n')
        functions.append("""
async function request(method: string, path: string, body?: any) {
  const options: RequestInit = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) options.body = JSON.stringify(body);
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
  if (response.status === 204) return null;
  return response.json();
}
""")

        for endpoint in endpoints:
            method = endpoint["method"]
            path = endpoint["path"]
            operation_id = endpoint.get("operationId", "")
            summary = endpoint.get("summary", "")

            path_params = re.findall(r"\{(\w+)\}", path)

            params = ", ".join([f"{p}: number | string" for p in path_params])
            if method in ["POST", "PUT", "PATCH"]:
                params = f"{params}, {'data: any' if params else 'data: any'}"

            ts_path = re.sub(r"\{(\w+)\}", r"${\\1}", path)
            ts_path = ts_path.replace("\\1", "")

            for p in path_params:
                ts_path = ts_path.replace(f"${{{p.replace('', '')}}}", f"${{{p}}}")

            body_arg = ", data" if method in ["POST", "PUT", "PATCH"] else ""

            func = f"""
// {summary}
export async function {operation_id}({params}) {{
  return request("{method}", `{ts_path}`{body_arg});
}}"""
            functions.append(func)

        return "\n".join(functions)

    # =========================
    # LLM CALL
    # =========================
    def _call_llm(self, filename: str, page_code: str, endpoints: list) -> str:
        system_prompt = self.system_prompt_template.replace(
            "{endpoints}", json.dumps(endpoints, indent=2)
        ).replace(
            "{filename}", filename
        ).replace(
            "{page_code}", page_code
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Analyze the page '{filename}' and connect it to the backend API. Return ONLY the complete modified TypeScript React code, no explanation, no markdown, no backticks.")
        ]

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(messages)
                return self._clean_code(response.content)
            except Exception as e:
                last_error = e
                continue

        raise Exception(f"LLM call failed after 3 retries: {str(last_error)}")

    # =========================
    # CLEAN CODE
    # =========================
    def _clean_code(self, text: str) -> str:
        cleaned = re.sub(r"```(?:tsx|typescript|ts|jsx|js)?\s*", "", text)
        cleaned = cleaned.replace("```", "").strip()
        return cleaned

    # =========================
    # WRITE FILE
    # =========================
    def _write_file(self, relative_path: str, content: str):
        full_path = os.path.join(FRONTEND_PATH, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)