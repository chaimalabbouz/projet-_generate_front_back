"""Protège la règle architecturale : les champs lourds ne voyagent pas."""
import json
from shared.state import GraphState


def test_heavy_fields_excluded_from_transport():
    state = GraphState(
        user_input="test",
        task_queue=[{"order": 1, "file": "app/models/x.py", "type": "model"}],
        generated_files={"app/models/x.py": "class X: pass"},
        test_results={"X": {"status": "passed"}},
        frontend_pages={"Home.jsx": "<div/>"},
    )

    transported = state.to_transport()

    assert "generated_files" not in transported
    assert "test_results" not in transported
    assert "frontend_pages" not in transported
    assert transported["task_queue"] is not None


def test_state_survives_json_roundtrip():
    """Le state doit traverser Redis sans perte."""
    state = GraphState(
        user_input="test",
        openapi_spec={"openapi": "3.0.0", "paths": {}},
        task_queue=[{"order": 1, "file": "a.py", "type": "model", "status": "pending"}],
        dependency_graph={"Doctor": []},
    )

    raw = json.dumps(state.to_transport())
    rebuilt = GraphState(**json.loads(raw))

    assert rebuilt.task_queue == state.task_queue
    assert rebuilt.openapi_spec == state.openapi_spec
    assert rebuilt.dependency_graph == state.dependency_graph