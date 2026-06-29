"""
Deterministic database seed generator (NODE, not an agent).

Reads the planner's task_queue (model tasks) + dependency_graph and produces
app/seed.py: a script that fills the database with valid rows.

Why deterministic (same reasons as the test generator):
  - inserts entities in dependency order (parents before children)
  - fills EVERY NOT NULL column from the model spec  -> no missing-field crash
  - resolves foreign keys to REAL parent ids          -> no IntegrityError
  - image-like string columns get a working placeholder URL (no broken images)

No LLM. Same plan in -> same seed out.
"""

import os
from typing import Dict, List, Any, Optional


# columns whose NAME hints they hold an image URL -> use a real placeholder image
_IMAGE_HINTS = ("image", "img", "photo", "picture", "avatar", "thumbnail", "logo")


class SeedGenerator:
    def __init__(self, task_queue: List[dict], dependency_graph: Optional[dict] = None,
                 rows_per_entity: int = 5):
        self.task_queue = task_queue or []
        self.dependency_graph = dependency_graph or {}
        self.rows = rows_per_entity
        self._models: Dict[str, dict] = {}   # entity -> model task (fields + file)
        self._index()

    def _index(self) -> None:
        for t in self.task_queue:
            if t.get("type") == "model":
                self._models[t.get("entity")] = t

    # ---------- lookups ----------
    def _model_fields(self, entity: str) -> list:
        return self._models.get(entity, {}).get("fields", [])

    def _module_path(self, entity: str) -> str:
        # Use the REAL file path from the plan (handles order_item.py vs orderitem).
        f = self._models.get(entity, {}).get("file", f"app/models/{entity.lower()}.py")
        return f.replace("/", ".").replace("\\", ".")[:-3]  # strip ".py"

    def _fk_parents(self, entity: str) -> List[tuple]:
        out = []
        for fld in self._model_fields(entity):
            fk = fld.get("foreign_key")
            if fk:
                out.append((fld["name"], fk.split(".")[0]))
        return out

    @staticmethod
    def _is_auto(field: dict) -> bool:
        return bool(field.get("primary_key")) or "default" in field

    # ---------- ordering ----------
    def _seed_order(self) -> List[str]:
        ordered: List[str] = []

        def visit(e: str):
            for _, parent in self._fk_parents(e):
                visit(parent)
            if e not in ordered:
                ordered.append(e)

        for entity in self._models:
            visit(entity)
        return ordered

    # ---------- value generation ----------
    def _value_expr(self, field: dict, entity: str) -> str:
        """Return a Python expression (as string) for this column at loop index i."""
        name = field["name"]
        ftype = (field.get("type") or "").split("(")[0]
        lname = name.lower()

        # image columns -> a real, always-available placeholder image
        if ftype == "String" and any(h in lname for h in _IMAGE_HINTS):
            return '"https://picsum.photos/seed/" + str(i) + "/600/400"'

        if ftype in ("String", "Text"):
            if "email" in lname:
                return f'"{entity.lower()}" + str(i) + "@example.com"'
            if "phone" in lname:
                return '"+10000000" + str(i).zfill(3)'
            if "url" in lname:
                return '"https://example.com/" + str(i)'
            if name in ("name", "title", "full_name", "order_number"):
                return f'"{entity} " + str(i + 1)'
            return f'"{name} " + str(i + 1)'

        if ftype in ("Integer", "BigInteger", "SmallInteger"):
            return "(i + 1) * 10"
        if ftype in ("Float", "Numeric"):
            return "round((i + 1) * 9.99, 2)"
        if ftype == "Boolean":
            return "True"
        return '"value"'

    # ---------- code emission ----------
    def _gen_imports(self) -> str:
        order = self._seed_order()
        lines = ["from app.database import Base, engine, SessionLocal"]
        for e in order:
            lines.append(f"from {self._module_path(e)} import {e}")
        return "\n".join(lines)

    def _gen_entity_block(self, entity: str) -> str:
        fks = {n: p for n, p in self._fk_parents(entity)}
        kw_lines = []
        for f in self._model_fields(entity):
            if self._is_auto(f):
                continue
            name = f["name"]
            if name in fks:
                parent = fks[name]
                # cycle through already-created parents
                kw_lines.append(
                    f'                {name}=created["{parent}"][i % len(created["{parent}"])].id,'
                )
            else:
                kw_lines.append(f"                {name}={self._value_expr(f, entity)},")
        kwargs = "\n".join(kw_lines)
        return (
            f'        created["{entity}"] = []\n'
            f"        for i in range(ROWS):\n"
            f"            obj = {entity}(\n"
            f"{kwargs}\n"
            f"            )\n"
            f"            db.add(obj)\n"
            f"            db.commit()\n"
            f"            db.refresh(obj)\n"
            f'            created["{entity}"].append(obj)\n'
            f'        print(f"  seeded {{ROWS}} {entity}")\n'
        )

    def generate(self) -> str:
        order = self._seed_order()
        blocks = "\n".join(self._gen_entity_block(e) for e in order)
        return (
            "# AUTO-GENERATED deterministic seed. Inserts rows in dependency order,\n"
            "# fills every NOT NULL column, resolves foreign keys to real parent ids.\n\n"
            f"{self._gen_imports()}\n\n"
            f"ROWS = {self.rows}\n\n"
            "def seed():\n"
            "    Base.metadata.create_all(bind=engine)\n"
            "    db = SessionLocal()\n"
            "    try:\n"
            "        created = {}\n\n"
            f"{blocks}\n"
            '        print("Seed complete.")\n'
            "    finally:\n"
            "        db.close()\n\n"
            'if __name__ == "__main__":\n'
            "    seed()\n"
        )


# =========================
# LANGGRAPH NODE (replaces the LLM SeedAgent)
# =========================
class SeedNode:
    def __init__(self, project_path: str, rows_per_entity: int = 5):
        self.project_path = project_path
        self.rows = rows_per_entity

    def run(self, state):
        try:
            if not state.task_queue:
                raise ValueError("task_queue is missing from state")

            generator = SeedGenerator(state.task_queue, state.dependency_graph, self.rows)
            seed_code = generator.generate()

            out_path = os.path.join(self.project_path, "app", "seed.py")
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(seed_code)

            if state.generated_files is None:
                state.generated_files = {}
            state.generated_files["app/seed.py"] = seed_code
            state.workflow_state = "seed_done"
            print("  \u2713 Generated: app/seed.py")

        except Exception as e:
            state.workflow_state = "seed_failed"
            state.error_log = (state.error_log or "") + f"\n[SEED NODE ERROR] {str(e)}"

        return state