"""
Frontend API-client generator (NODE, not an agent).

100% deterministic. Reads the OpenAPI spec (state.openapi_spec) and produces a
TypeScript file `src/api/client.ts` containing:

  - one TS interface per schema (Product, ProductCreate, ...)
  - one typed async function per endpoint (getProductById, createProduct, ...)

No LLM. Same spec in -> same client out. This is the foundation the binding
agent consumes: the agent never builds a fetch call, it only CALLS these
functions.
"""

import os
from typing import Dict, Any, List, Optional


# OpenAPI primitive -> TypeScript type
def _ref_name(ref: str) -> str:
    # "#/components/schemas/Product" -> "Product"
    return ref.split("/")[-1]


def _ts_type(prop: Dict[str, Any]) -> str:
    if not isinstance(prop, dict):
        return "any"
    if "$ref" in prop:
        return _ref_name(prop["$ref"])
    t = prop.get("type")
    if t in ("integer", "number"):
        return "number"
    if t == "string":
        return "string"
    if t == "boolean":
        return "boolean"
    if t == "array":
        return _ts_type(prop.get("items", {})) + "[]"
    if t == "object":
        return "Record<string, any>"
    return "any"


def _camel(snake: str) -> str:
    # create_product -> createProduct ; get_product_by_id -> getProductById
    parts = snake.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


class ApiClientGenerator:
    def __init__(self, openapi_spec: Dict[str, Any]):
        self.spec = openapi_spec or {}
        self.schemas = self.spec.get("components", {}).get("schemas", {})
        self.paths = self.spec.get("paths", {})

    # ---------------- TS interfaces ----------------
    def _gen_interface(self, name: str, schema: Dict[str, Any]) -> str:
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        # Response schemas have no "required" -> treat every field as present.
        has_required = "required" in schema
        lines = [f"export interface {name} {{"]
        for field, prop in props.items():
            optional = has_required and field not in required
            lines.append(f"  {field}{'?' if optional else ''}: {_ts_type(prop)};")
        lines.append("}")
        return "\n".join(lines)

    def _gen_all_interfaces(self) -> str:
        return "\n\n".join(
            self._gen_interface(name, schema) for name, schema in self.schemas.items()
        )

    # ---------------- endpoint helpers ----------------
    def _success_response_type(self, operation: Dict[str, Any]) -> str:
        responses = operation.get("responses", {})
        for code in ("200", "201", "202"):
            if code in responses:
                content = responses[code].get("content", {})
                schema = content.get("application/json", {}).get("schema")
                if not schema:
                    return "void"
                if "$ref" in schema:
                    return _ref_name(schema["$ref"])
                if schema.get("type") == "array":
                    return _ts_type(schema.get("items", {})) + "[]"
                return _ts_type(schema)
        if "204" in responses:
            return "void"
        return "void"

    def _body_type(self, operation: Dict[str, Any]) -> Optional[str]:
        rb = operation.get("requestBody")
        if not rb:
            return None
        schema = rb.get("content", {}).get("application/json", {}).get("schema", {})
        if "$ref" in schema:
            return _ref_name(schema["$ref"])
        return None

    def _path_params(self, operation: Dict[str, Any]) -> List[str]:
        out = []
        for p in operation.get("parameters", []):
            if p.get("in") == "path":
                out.append(p.get("name"))
        return out

    # ---------------- one function per endpoint ----------------
    def _gen_function(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        op_id = operation.get("operationId")
        if not op_id:
            return ""
        fn_name = _camel(op_id)
        ret = self._success_response_type(operation)
        body_type = self._body_type(operation)
        path_params = self._path_params(operation)

        # build typed args: path params (number) first, then body
        args = [f"{name}: number" for name in path_params]
        if body_type:
            args.append(f"data: {body_type}")
        args_str = ", ".join(args)

        # turn /products/{id} into a JS template `/products/${id}`
        url = path
        for name in path_params:
            url = url.replace("{" + name + "}", "${" + name + "}")

        # fetch options
        opts = [f'method: "{method.upper()}"']
        if body_type:
            opts.append('headers: { "Content-Type": "application/json" }')
            opts.append("body: JSON.stringify(data)")
        opts_str = ", ".join(opts)

        lines = [f"export async function {fn_name}({args_str}): Promise<{ret}> {{"]
        if method.upper() == "GET":
            lines.append(f"  const res = await fetch(`${{BASE_URL}}{url}`);")
        else:
            lines.append(f"  const res = await fetch(`${{BASE_URL}}{url}`, {{ {opts_str} }});")
        lines.append('  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);')
        if ret == "void":
            lines.append("  return;")
        else:
            lines.append("  return res.json();")
        lines.append("}")
        return "\n".join(lines)

    def _gen_all_functions(self) -> str:
        blocks = []
        for path, methods in self.paths.items():
            for method, operation in methods.items():
                if method.lower() not in ("get", "post", "put", "patch", "delete"):
                    continue
                fn = self._gen_function(path, method, operation)
                if fn:
                    blocks.append(fn)
        return "\n\n".join(blocks)

    # ---------------- public ----------------
    def generate(self, base_url: str = "http://localhost:8000") -> str:
        header = (
            "// AUTO-GENERATED from the OpenAPI contract. Do not edit by hand.\n"
            "// Regenerated deterministically; every endpoint maps 1:1 to the backend.\n\n"
            f'const BASE_URL = "{base_url}";\n'
        )
        return (
            header
            + "\n// ===== Types =====\n\n"
            + self._gen_all_interfaces()
            + "\n\n// ===== API functions =====\n\n"
            + self._gen_all_functions()
            + "\n"
        )


# =========================
# LANGGRAPH NODE
# =========================
class FrontendApiNode:
    """
    Graph node. Reads state.openapi_spec, writes src/api/client.ts into the
    frontend project, and stores the code in state.frontend_api_service.

    `project_path` is the GENERATED_PROJECT_PATH (the repo root that holds both
    the backend at the root and the `frontend/` subfolder). The client is
    written to:  <project_path>/frontend/src/api/client.ts
    """

    def __init__(self, project_path: Optional[str] = None,
                 base_url: str = "http://localhost:8000",
                 frontend_subdir: str = "frontend"):
        # project_path: GENERATED_PROJECT_PATH. If None, the node only fills
        # state.frontend_api_service (no disk write).
        self.project_path = project_path
        self.base_url = base_url
        self.frontend_subdir = frontend_subdir

    def run(self, state):
        try:
            if not state.openapi_spec:
                raise ValueError("openapi_spec is missing from state")

            generator = ApiClientGenerator(state.openapi_spec)
            client_code = generator.generate(self.base_url)

            state.frontend_api_service = client_code

            if self.project_path:
                out_path = os.path.join(
                    self.project_path, self.frontend_subdir, "src", "api", "client.ts"
                )
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(client_code)
                print(f"  \u2713 Generated: {self.frontend_subdir}/src/api/client.ts")

            state.workflow_state = "frontend_api_done"

        except Exception as e:
            state.workflow_state = "frontend_api_failed"
            state.error_log = (state.error_log or "") + f"\n[FRONTEND API NODE ERROR] {str(e)}"

        return state