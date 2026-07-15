"""
Corrige tous les imports dans services/design/ après le déplacement.
Lance : python fix_imports.py
"""
import re
from pathlib import Path

ROOT = Path("services/frontend")

REPLACEMENTS = [
    # figma_services -> services.design.figma_services
    (r"\bfrom figma_services\.", "from services.design.figma_services."),
    (r"\bimport figma_services\.", "import services.design.figma_services."),
    (r"\bfrom figma_services import", "from services.design.figma_services import"),

    # config.settings -> shared.settings
    (r"\bfrom config\.settings import", "from shared.settings import"),
    (r"\bfrom config import settings", "from shared import settings"),

    # orchestrator.state -> shared.state
    (r"\bfrom orchestrator\.state import", "from shared.state import"),
]

changed_files = 0
total_changes = 0

for path in ROOT.rglob("*.py"):
    if "__pycache__" in str(path):
        continue

    original = path.read_text(encoding="utf-8")
    content = original
    file_changes = 0

    for pattern, replacement in REPLACEMENTS:
        content, n = re.subn(pattern, replacement, content)
        file_changes += n

    if content != original:
        path.write_text(content, encoding="utf-8")
        changed_files += 1
        total_changes += file_changes
        print(f"  ✓ {path}  ({file_changes} imports)")

print(f"\n{changed_files} fichiers modifiés, {total_changes} imports corrigés.")