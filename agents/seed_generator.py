"""
Deterministic database seed generator (NODE, not an agent).

Structure = 100% deterministic (order, FK, PK, timestamps).
Only FREE-TEXT scalar values are produced by an LLM (Groq / llama-3.3-70b),
with strict JSON parsing, length truncation, and a deterministic fallback
everywhere. No LLM key -> pure deterministic (same as before).

Images: themed placeholder URLs (loremflickr) with a UNIQUE lock per
entity/column/row -> varied, realistic images. Pair with an `onerror`
fallback to placehold.co in the frontend so the layout never breaks.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import GROQ_API_KEY


# Model used ONLY to produce realistic free-text values.
SEED_MODEL = "llama-3.3-70b-versatile"

# columns whose NAME hints they hold an image URL -> themed placeholder image
_IMAGE_HINTS = ("image", "img", "photo", "picture", "avatar", "thumbnail", "logo")


class SeedGenerator:
    def __init__(self, task_queue: List[dict], dependency_graph: Optional[dict] = None,
                 rows_per_entity: int = 5):
        self.task_queue = task_queue or []
        self.dependency_graph = dependency_graph or {}
        self.rows = rows_per_entity
        self._models: Dict[str, dict] = {}                 # entity -> model task
        self._llm_cache: Dict[str, Dict[str, list]] = {}   # entity -> {col -> [values]}
        self._index()

        # LLM is optional. If no key / init fails -> deterministic fallback.
        self.llm = None
        if GROQ_API_KEY:
            try:
                self.llm = ChatGroq(
                    api_key=GROQ_API_KEY,
                    model=SEED_MODEL,
                    temperature=0.5,
                )
            except Exception:
                self.llm = None

    def _index(self) -> None:
        for t in self.task_queue:
            if t.get("type") == "model":
                self._models[t.get("entity")] = t

    # ---------- lookups ----------
    def _model_fields(self, entity: str) -> list:
        return self._models.get(entity, {}).get("fields", [])

    def _module_path(self, entity: str) -> str:
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

    # ---------- free-text detection ----------
    def _is_free_text(self, field: dict) -> bool:
        ftype = (field.get("type") or "").split("(")[0]
        if ftype not in ("String", "Text"):
            return False
        lname = field["name"].lower()
        if any(h in lname for h in _IMAGE_HINTS):
            return False
        if "email" in lname or "phone" in lname or "url" in lname:
            return False
        return True

    def _max_len(self, field: dict) -> Optional[int]:
        m = re.search(r"String\((\d+)\)", field.get("type") or "")
        return int(m.group(1)) if m else None

    # ---------- LLM values (cached per entity) ----------
    def _clean_json(self, text: str) -> str:
        cleaned = re.sub(r"```(?:json)?\s*", "", text)
        return cleaned.replace("```", "").strip()

    def _fallback_value(self, field: dict, entity: str, i: int) -> str:
        name = field["name"]
        if name in ("name", "title", "full_name", "order_number"):
            return f"{entity} {i + 1}"
        return f"{name} {i + 1}"

    def _normalize(self, raw: Any, field: dict, entity: str) -> Optional[list]:
        if not isinstance(raw, list) or not raw:
            return None
        maxlen = self._max_len(field)
        vals = []
        for v in raw:
            s = str(v)
            if maxlen:
                s = s[:maxlen]
            vals.append(s)
        # pad if the LLM returned fewer than ROWS
        for i in range(len(vals), self.rows):
            s = self._fallback_value(field, entity, i)
            if maxlen:
                s = s[:maxlen]
            vals.append(s)
        return vals[:self.rows]

    def _ensure_llm_values(self, entity: str) -> None:
        if entity in self._llm_cache:
            return
        self._llm_cache[entity] = {}
        if self.llm is None:
            return

        cols = [f for f in self._model_fields(entity) if self._is_free_text(f)]
        if not cols:
            return

        col_desc = "\n".join(
            f'- {f["name"]} ({(f.get("type") or "String")})' for f in cols
        )
        system = SystemMessage(content=(
            "You generate realistic, coherent seed data for a database. "
            "Return ONLY valid JSON, no markdown, no backticks, no explanation."
        ))
        human = HumanMessage(content=(
            f'Entity: "{entity}". Generate exactly {self.rows} realistic rows.\n'
            f"For EACH column below, return a JSON array of exactly {self.rows} values.\n"
            "Values MUST match the column meaning, be realistic and plausible, "
            "and be consistent within the same row index (index k across columns "
            "describes the same real-world object).\n\n"
            f"Columns:\n{col_desc}\n\n"
            'Return JSON exactly like: {"column_name": ["v1", "v2", ...], ...}'
        ))

        try:
            resp = self.llm.invoke([system, human])
            data = json.loads(self._clean_json(resp.content))
        except Exception:
            return  # -> deterministic fallback for this entity

        result: Dict[str, list] = {}
        for f in cols:
            vals = self._normalize(data.get(f["name"]), f, entity)
            if vals:
                result[f["name"]] = vals
        self._llm_cache[entity] = result

    # ---------- image helpers ----------
    def _image_keyword(self, entity: str, colname: str) -> str:
        lname = colname.lower()
        if any(k in lname for k in ("avatar", "author", "profile")):
            return "portrait,face"
        return entity.lower()

    def _image_expr(self, entity: str, colname: str) -> str:
        """Themed loremflickr URL with a UNIQUE lock per entity/column/row."""
        kw = self._image_keyword(entity, colname)
        base_lock = abs(hash(f"{entity}:{colname}")) % 1000
        return (
            f'"https://loremflickr.com/600/400/{kw}?lock=" + str({base_lock} + i)'
        )

    # ---------- value generation ----------
    def _value_expr(self, field: dict, entity: str) -> str:
        """Return a Python expression (as string) for this column at loop index i."""
        name = field["name"]
        ftype = (field.get("type") or "").split("(")[0]
        lname = name.lower()

        # image columns -> themed, varied, always-available placeholder image
        if ftype == "String" and any(h in lname for h in _IMAGE_HINTS):
            return self._image_expr(entity, name)

        # free text -> LLM values (indexed list literal), else deterministic
        if self._is_free_text(field):
            self._ensure_llm_values(entity)
            vals = self._llm_cache.get(entity, {}).get(name)
            if vals:
                literals = ", ".join(repr(v) for v in vals)
                return f"[{literals}][i]"

        # ---- deterministic fallback (unchanged logic) ----
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
        if ftype == "DateTime":
            return "datetime.utcnow()"
        if ftype == "Date":
            return "datetime.utcnow().date()"
        return '"value"'

    # ---------- code emission ----------
    def _gen_imports(self) -> str:
        order = self._seed_order()
        lines = [
            "from datetime import datetime",
            "from app.database import Base, engine, SessionLocal",
        ]
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
            "# AUTO-GENERATED seed. Structure deterministic (order, FK, NOT NULL);\n"
            "# free-text values by LLM (fallback deterministic); themed varied images.\n\n"
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
# LANGGRAPH NODE (unchanged behavior: generates + writes app/seed.py)
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