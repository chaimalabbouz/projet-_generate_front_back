"""
Deterministic pytest generator for CRUD FastAPI entities.

Reads the planner's task_queue (model / schema / route tasks) and produces a
COMPLETE integration-test file for one entity, with NO LLM involved.

Why this kills the hallucinations for good:
  - HTTP status codes come from route functions[].status_code   -> no more 201 vs 200
  - required columns come from model fields[] (nullable == False) -> no more missing NOT NULL field
  - FK parent chains are seeded from model fields[].foreign_key   -> parents are ALWAYS created
    fully, recursively (Cuisine -> Recipe -> Review), so a partial parent is impossible.

There is no model that "decides" anything. Same input -> same output, every time.
"""

from typing import Dict, List, Optional, Tuple


# SQLAlchemy column type -> python literal (used when seeding rows via the ORM)
_SQLA_VALUES = {
    "Integer": "1",
    "BigInteger": "1",
    "SmallInteger": "1",
    "Float": "1.5",
    "Numeric": "1.5",
    "Boolean": "True",
    "String": '"test_string"',
    "Text": '"test_text"',
}

# pydantic/python type -> python literal (used in JSON request payloads)
_PY_VALUES = {
    "int": "1",
    "float": "1.5",
    "bool": "True",
    "str": '"test_string"',
}


class TestGenerator:
    def __init__(self, task_queue: List[dict], dependency_graph: Optional[dict] = None):
        self.task_queue = task_queue or []
        self.dependency_graph = dependency_graph or {}
        self._models: Dict[str, list] = {}
        self._schemas: Dict[str, Dict[str, list]] = {}
        self._routes: Dict[str, list] = {}
        self._index()

    # ---------------- indexing ----------------
    def _index(self) -> None:
        for t in self.task_queue:
            ttype, entity = t.get("type"), t.get("entity")
            if ttype == "model":
                self._models[entity] = t.get("fields", [])
            elif ttype == "schema":
                self._schemas[entity] = {
                    s["name"]: s.get("fields", []) for s in t.get("schemas", [])
                }
            elif ttype == "route":
                self._routes[entity] = t.get("functions", [])

    # ---------------- lookups ----------------
    def _model_fields(self, entity: str) -> list:
        return self._models.get(entity, [])

    def _create_schema_fields(self, entity: str) -> list:
        return self._schemas.get(entity, {}).get(f"{entity}Create", [])

    def _route_functions(self, entity: str) -> list:
        return self._routes.get(entity, [])

    def _fk_fields(self, entity: str) -> List[Tuple[str, str]]:
        """[(field_name, parent_entity), ...] for FK columns of `entity`."""
        out = []
        for f in self._model_fields(entity):
            fk = f.get("foreign_key")
            if fk:
                out.append((f["name"], fk.split(".")[0]))
        return out

    @staticmethod
    def _is_auto(field: dict) -> bool:
        # PK is auto-increment; anything with a server/python default (timestamps) is auto-filled
        return bool(field.get("primary_key")) or "default" in field

    def _value_for_sqla(self, sqla_type: Optional[str]) -> str:
        if sqla_type in _SQLA_VALUES:
            return _SQLA_VALUES[sqla_type]
        base = (sqla_type or "").split("(")[0]
        return _SQLA_VALUES.get(base, '"test_string"')

    # ---------------- seed helpers ----------------
    def _seed_order(self, entity: str) -> List[str]:
        """`entity` plus all transitive FK parents, parents first."""
        ordered: List[str] = []

        def visit(e: str) -> None:
            for _, parent in self._fk_fields(e):
                visit(parent)
            if e not in ordered:
                ordered.append(e)

        visit(entity)
        return ordered

    def _gen_seed_helper(self, entity: str) -> str:
        parent_lines, kwargs = [], []
        for f in self._model_fields(entity):
            if self._is_auto(f):
                continue
            name = f["name"]
            fk = f.get("foreign_key")
            if fk:
                parent = fk.split(".")[0]
                var = name[:-3] if name.endswith("_id") else parent.lower()
                parent_lines.append(f"    {var} = _create_{parent.lower()}(db)")
                kwargs.append(f"{name}={var}.id")
            else:
                kwargs.append(f"{name}={self._value_for_sqla(f.get('type'))}")

        body = ("\n".join(parent_lines) + "\n") if parent_lines else ""
        return (
            f"def _create_{entity.lower()}(db):\n"
            f"{body}"
            f"    obj = {entity}({', '.join(kwargs)})\n"
            f"    db.add(obj)\n"
            f"    db.commit()\n"
            f"    db.refresh(obj)\n"
            f"    return obj\n"
        )

    # ---------------- classify endpoints ----------------
    def _classify(self, fn: dict) -> Optional[str]:
        method = (fn.get("method") or "").upper()
        path = fn.get("path") or ""
        if method == "POST":
            return "create"
        if method == "GET":
            if "{" not in path:
                return "list"
            return "get_by_id" if path.rstrip("/").split("/")[-1] == "{id}" else "relational"
        if method in ("PUT", "PATCH"):
            return "update"
        if method == "DELETE":
            return "delete"
        return None

    # ---------------- per-test generators ----------------
    def _build_payload(self, entity: str):
        fk_map = {n: p for n, p in self._fk_fields(entity)}
        seed_lines, capture_lines, items = [], [], []
        for f in self._create_schema_fields(entity):
            name = f["name"]
            if name in fk_map:
                parent = fk_map[name]
                var = name[:-3] if name.endswith("_id") else parent.lower()
                seed_lines.append(f"    {var} = _create_{parent.lower()}(db)")
                capture_lines.append(f"    {name}_value = {var}.id")
                items.append(f'"{name}": {name}_value')
            else:
                items.append(f'"{name}": {_PY_VALUES.get(f.get("type"), chr(34) + "test_string" + chr(34))}')
        return "{" + ", ".join(items) + "}", seed_lines, capture_lines, set(fk_map)

    def _gen_create(self, entity: str, fn: dict) -> str:
        op, path = fn["operationId"], fn["path"]
        status = fn.get("status_code", 201)
        payload, seed, capture, fk_names = self._build_payload(entity)
        lines = [f"def test_{op}():"]
        if seed:
            lines.append("    db = TestingSessionLocal()")
            lines += seed + capture
            lines.append("    db.close()")
        lines += [
            f"    payload = {payload}",
            f'    response = client.post("{path}", json=payload)',
            f"    assert response.status_code == {status}",
            "    data = response.json()",
            '    assert "id" in data',
        ]
        for f in self._create_schema_fields(entity):
            if f["name"] in fk_names:
                continue
            val = _PY_VALUES.get(f.get("type"), '"test_string"')
            lines.append(f'    assert data["{f["name"]}"] == {val}')
        return "\n".join(lines) + "\n"

    def _gen_list(self, entity: str, fn: dict) -> str:
        op, path = fn["operationId"], fn["path"]
        return "\n".join([
            f"def test_{op}():",
            "    db = TestingSessionLocal()",
            f"    _create_{entity.lower()}(db)",
            "    db.close()",
            f'    response = client.get("{path}")',
            "    assert response.status_code == 200",
            "    assert isinstance(response.json(), list)",
            "    assert len(response.json()) >= 1",
        ]) + "\n"

    def _gen_get_by_id(self, entity: str, fn: dict) -> str:
        op, path = fn["operationId"], fn["path"]
        ok_url = path.replace("{id}", "{obj_id}")
        nf_url = path.replace("{id}", "999999")
        return "\n".join([
            f"def test_{op}():",
            "    db = TestingSessionLocal()",
            f"    obj = _create_{entity.lower()}(db)",
            "    obj_id = obj.id",
            "    db.close()",
            f'    response = client.get(f"{ok_url}")',
            "    assert response.status_code == 200",
            '    assert response.json()["id"] == obj_id',
            "",
            f"def test_{op}_not_found():",
            f'    response = client.get("{nf_url}")',
            "    assert response.status_code == 404",
        ]) + "\n"

    def _gen_relational(self, entity: str, fn: dict) -> str:
        op, path = fn["operationId"], fn["path"]
        fks = self._fk_fields(entity)
        first_seg = path.strip("/").split("/")[0]
        fk_field = fks[0][0] if fks else "id"
        for fname, parent in fks:
            if parent.lower() in first_seg:
                fk_field = fname
                break
        url = path.replace("{id}", "{parent_id}")
        return "\n".join([
            f"def test_{op}():",
            "    db = TestingSessionLocal()",
            f"    obj = _create_{entity.lower()}(db)",
            f"    parent_id = obj.{fk_field}",
            "    db.close()",
            f'    response = client.get(f"{url}")',
            "    assert response.status_code == 200",
            "    assert isinstance(response.json(), list)",
        ]) + "\n"

    def _gen_update(self, entity: str, fn: dict) -> str:
        op, path = fn["operationId"], fn["path"]
        status = fn.get("status_code", 200)
        ok_url = path.replace("{id}", "{obj_id}")
        fk_names = {n for n, _ in self._fk_fields(entity)}
        # build an UPDATED payload: reuse the seeded row's FK ids, change scalars
        updated = {"str": '"updated_string"', "int": "2", "bool": "False", "float": "2.5"}
        items, checks = [], []
        for f in self._create_schema_fields(entity):
            name, ftype = f["name"], f.get("type")
            if name in fk_names:
                items.append(f'"{name}": obj.{name}')
            else:
                val = updated.get(ftype, '"updated_string"')
                items.append(f'"{name}": {val}')
                checks.append(f'    assert data["{name}"] == {val}')
        payload = "{" + ", ".join(items) + "}"
        lines = [
            f"def test_{op}():",
            "    db = TestingSessionLocal()",
            f"    obj = _create_{entity.lower()}(db)",
            "    obj_id = obj.id",
            f"    payload = {payload}",
            "    db.close()",
            f'    response = client.put(f"{ok_url}", json=payload)',
            f"    assert response.status_code == {status}",
            "    data = response.json()",
        ] + checks
        return "\n".join(lines) + "\n"

    def _gen_delete(self, entity: str, fn: dict) -> str:
        op, path = fn["operationId"], fn["path"]
        status = fn.get("status_code", 204)
        ok_url = path.replace("{id}", "{obj_id}")
        nf_url = path.replace("{id}", "999999")
        return "\n".join([
            f"def test_{op}():",
            "    db = TestingSessionLocal()",
            f"    obj = _create_{entity.lower()}(db)",
            "    obj_id = obj.id",
            "    db.close()",
            f'    response = client.delete(f"{ok_url}")',
            f"    assert response.status_code == {status}",
            "",
            f"def test_{op}_not_found():",
            f'    response = client.delete("{nf_url}")',
            "    assert response.status_code == 404",
        ]) + "\n"

    # ---------------- header ----------------
    def _gen_header(self, entity: str) -> str:
        model_imports = "\n".join(
            f"from app.models.{e.lower()} import {e}" for e in self._seed_order(entity)
        )
        return (
            "import pytest\n"
            "from fastapi import FastAPI\n"
            "from fastapi.testclient import TestClient\n"
            "from sqlalchemy import create_engine\n"
            "from sqlalchemy.orm import sessionmaker\n"
            "from app.database import Base, get_db\n"
            f"from app.routes.{entity.lower()} import router\n"
            f"{model_imports}\n\n"
            'SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"\n'
            "engine = create_engine(\n"
            "    SQLALCHEMY_TEST_DATABASE_URL,\n"
            '    connect_args={"check_same_thread": False},\n'
            ")\n"
            "TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n\n"
            "app = FastAPI()\n"
            "app.include_router(router)\n\n\n"
            "def override_get_db():\n"
            "    db = TestingSessionLocal()\n"
            "    try:\n"
            "        yield db\n"
            "    finally:\n"
            "        db.close()\n\n\n"
            "app.dependency_overrides[get_db] = override_get_db\n\n\n"
            "@pytest.fixture(autouse=True)\n"
            "def setup_database():\n"
            "    Base.metadata.create_all(bind=engine)\n"
            "    yield\n"
            "    Base.metadata.drop_all(bind=engine)\n\n\n"
            "client = TestClient(app)\n"
        )

    # ---------------- public ----------------
    def generate(self, entity: str) -> str:
        parts = [self._gen_header(entity)]

        parts.append("# --- ORM seed helpers (full NOT NULL columns, FK chain auto-built) ---")
        for e in self._seed_order(entity):
            parts.append(self._gen_seed_helper(e))

        parts.append("# --- tests (status codes & fields derived from the plan) ---")
        dispatch = {
            "create": self._gen_create,
            "list": self._gen_list,
            "get_by_id": self._gen_get_by_id,
            "relational": self._gen_relational,
            "update": self._gen_update,
            "delete": self._gen_delete,
        }
        for fn in self._route_functions(entity):
            kind = self._classify(fn)
            if kind in dispatch:
                parts.append(dispatch[kind](entity, fn))

        return "\n".join(parts).rstrip() + "\n"