"""Les graphes doivent se compiler : câblage + imports OK.
On ne les INVOQUE pas — aucun LLM, aucun réseau."""
import os

os.environ.setdefault("MISTRAL_API_KEY", "fake-key-for-ci")
os.environ.setdefault("GROQ_API_KEY", "fake-key-for-ci")


def test_planner_graph_compiles():
    from services.planner.graph import create_planner_graph
    assert create_planner_graph() is not None


def test_backend_graph_compiles():
    from services.backend.graph import create_backend_graph
    assert create_backend_graph() is not None


def test_frontend_graph_compiles():
    from services.frontend.graph import create_frontend_graph
    assert create_frontend_graph() is not None