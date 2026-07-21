"""Chaque skill référencée dans un index doit exister sur le disque.
Attrape les fichiers manquants ou exclus par .dockerignore."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKILL_DIRS = [
    ROOT / "services" / "backend" / "prompts" / "skills",
    ROOT / "services" / "frontend" / "prompts" / "skills",
]


def _referenced_files(index_path: Path):
    """Extrait les chemins entries/xxx.md cités dans l'index."""
    content = index_path.read_text(encoding="utf-8")
    return re.findall(r"entries/([\w\-]+\.md)", content)


def test_skill_indexes_exist():
    for d in SKILL_DIRS:
        if d.exists():
            assert (d / "index.md").exists(), f"index.md manquant dans {d}"


def test_all_referenced_skills_exist():
    for d in SKILL_DIRS:
        index = d / "index.md"
        if not index.exists():
            continue
        for fname in _referenced_files(index):
            path = d / "entries" / fname
            assert path.exists(), f"skill référencée mais absente : {path}"


def test_skill_files_are_not_empty():
    for d in SKILL_DIRS:
        entries = d / "entries"
        if not entries.exists():
            continue
        for f in entries.glob("*.md"):
            assert f.stat().st_size > 50, f"skill quasi vide : {f}"