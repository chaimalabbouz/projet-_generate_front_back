"""Les gardes : une tâche DOIT lever une exception si le state est en échec."""
import os
import pytest

os.environ.setdefault("MISTRAL_API_KEY", "fake-key-for-ci")
os.environ.setdefault("GROQ_API_KEY", "fake-key-for-ci")


class FakeGraph:
    """Remplace un vrai graphe LangGraph : renvoie un state figé."""
    def __init__(self, state):
        self._state = state

    def invoke(self, state, **kwargs):
        return self._state


def test_planner_guard_raises_on_failure(monkeypatch):
    from services.planner import tasks
    from shared.state import GraphState

    failed = GraphState(user_input="x")
    failed.workflow_state = "planning_failed"
    failed.error_log = "boom"

    monkeypatch.setattr(tasks, "get_graph", lambda: FakeGraph(failed))

    with pytest.raises(RuntimeError):
        tasks.run_planner({"user_input": "x"})


def test_planner_guard_passes_on_success(monkeypatch):
    from services.planner import tasks
    from shared.state import GraphState

    ok = GraphState(user_input="x")
    ok.workflow_state = "setup_done"
    ok.task_queue = [{"order": 1, "file": "a.py", "type": "model"}]

    monkeypatch.setattr(tasks, "get_graph", lambda: FakeGraph(ok))

    out = tasks.run_planner({"user_input": "x"})
    assert out["workflow_state"] == "setup_done"
    assert "generated_files" not in out       # champ lourd exclu du transport


def test_backend_guard_raises_when_nothing_passed(monkeypatch):
    """Si aucune entité n'a réussi, la tâche doit échouer."""
    from services.backend import tasks
    from shared.state import GraphState

    st = GraphState(user_input="x")
    st.workflow_state = "testing_done"
    st.task_queue = [
        {"type": "route", "entity": "Doctor", "status": "done", "test_status": "abandoned"},
    ]
    st.abandoned_entities = ["Doctor"]

    monkeypatch.setattr(tasks, "get_graph", lambda: FakeGraph(st))

    with pytest.raises(RuntimeError):
        tasks.run_backend({"user_input": "x"})


def test_backend_guard_passes_on_partial_success(monkeypatch):
    """4/5 entités réussies : le pipeline doit continuer."""
    from services.backend import tasks
    from shared.state import GraphState

    st = GraphState(user_input="x")
    st.workflow_state = "testing_done"
    st.task_queue = [
        {"type": "route", "entity": "Doctor", "status": "done", "test_status": "passed"},
        {"type": "route", "entity": "Blog", "status": "done", "test_status": "abandoned"},
    ]
    st.abandoned_entities = ["Blog"]

    monkeypatch.setattr(tasks, "get_graph", lambda: FakeGraph(st))

    out = tasks.run_backend({"user_input": "x"})
    assert out["workflow_state"] == "testing_done"