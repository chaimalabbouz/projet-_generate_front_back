"""
Test du service Design SANS Celery.
Lance : python -m services.design.run_local
"""
from pathlib import Path

from shared.state import GraphState
from shared.settings import INPUT_FILE, GENERATED_PROJECT_PATH
from services.design.graph import create_design_graph


def main():
    user_input = Path(INPUT_FILE).read_text(encoding="utf-8")
    state = GraphState(user_input=user_input)

    print("[DESIGN] démarrage du pipeline figma...\n")

    result = create_design_graph().invoke(state)
    if isinstance(result, dict):
        result = GraphState(**result)

    print("\n" + "=" * 50)
    print("workflow_state :", result.workflow_state)

    if result.workflow_state == "figma_generation_failed":
        print("❌ ÉCHEC")
        print(result.error_log)
        return

    print("✅ SUCCÈS")

    # vérification concrète : les pages sont-elles sur le disque ?
    pages_dir = Path(GENERATED_PROJECT_PATH) / "frontend" / "src" / "pages"
    if pages_dir.is_dir():
        pages = sorted(p.name for p in pages_dir.glob("*.tsx")) + \
                sorted(p.name for p in pages_dir.glob("*.jsx"))
        print(f"pages générées : {len(pages)}")
        for p in pages:
            print(f"  - {p}")
    else:
        print(f"⚠ aucun dossier de pages trouvé à {pages_dir}")


if __name__ == "__main__":
    main()