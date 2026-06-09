from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class GraphState(BaseModel):

    # ---------------- INPUT ----------------
    user_input: str
    stack: Optional[str] = None

    # ---------------- OPENAPI ----------------
    openapi_spec: Optional[Dict[str, Any]] = None

    # ---------------- PLANNING ----------------
    dependency_graph: Optional[Dict[str, Any]] = None

    file_plan: Optional[List[Dict[str, Any]]] = None

    task_queue: Optional[List[Dict[str, Any]]] = None

    # ---------------- CODE GENERATION ----------------
    generated_files: Optional[Dict[str, str]] = Field(
        default=None,
        description="path -> generated code"
    )

    # ---------------- FILESYSTEM ----------------
    filesystem_state: Optional[List[str]] = None

    # ---------------- TESTING ----------------
    test_results: Optional[Dict[str, Any]] = None

    error_log: Optional[str] = None

    # ---------------- FRONTEND ----------------
    frontend_spec: Optional[Dict[str, Any]] = None

    # ---------------- CONTROL FLOW ----------------
    workflow_state: Optional[str] = None

    retry_count: int = 0

    max_retries: int = 3

    # ---------------- TOOL CONTEXT ----------------
    tool_context: Optional[Dict[str, Any]] = None