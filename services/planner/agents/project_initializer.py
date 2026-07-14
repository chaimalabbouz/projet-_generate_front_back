import os
from shared.settings import GENERATED_PROJECT_PATH
from shared.state import GraphState

BACKEND_FOLDERS = [
    "app/models",
    "app/schemas",
    "app/services",
    "app/routes",
    "tests",
]

INIT_FILES = [
    "app/__init__.py",
    "app/models/__init__.py",
    "app/schemas/__init__.py",
    "app/services/__init__.py",
    "app/routes/__init__.py",
    "tests/__init__.py",
]

DATABASE_PY = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

REQUIREMENTS_TXT = """fastapi
uvicorn
sqlalchemy
pydantic
pytest
httpx
pytest-asyncio
"""


def initialize_project(state: GraphState) -> GraphState:
    try:
        os.makedirs(GENERATED_PROJECT_PATH, exist_ok=True)

        _create_backend_folders()
        _create_init_files()
        _create_database_file()
        _create_requirements_file()
        # venv + pip install : SUPPRIMÉS
        #   -> les dépendances sont dans l'image du worker Backend

        state.workflow_state = "setup_done"
        state.filesystem_state = _list_files()

    except Exception as e:
        state.workflow_state = "setup_failed"
        state.error_log = (state.error_log or "") + f"\n[SETUP ERROR] {str(e)}"

    return state


def _create_backend_folders():
    print("[SETUP] Creating backend folders...")
    for folder in BACKEND_FOLDERS:
        full_path = os.path.join(GENERATED_PROJECT_PATH, folder)
        os.makedirs(full_path, exist_ok=True)
        print(f"  ✓ {full_path}")


def _create_init_files():
    for init_file in INIT_FILES:
        full_path = os.path.join(GENERATED_PROJECT_PATH, init_file)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("")


def _create_database_file():
    full_path = os.path.join(GENERATED_PROJECT_PATH, "app", "database.py")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(DATABASE_PY)


def _create_requirements_file():
    full_path = os.path.join(GENERATED_PROJECT_PATH, "requirements.txt")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(REQUIREMENTS_TXT)


def _list_files() -> list:
    result = []
    for root, dirs, files in os.walk(GENERATED_PROJECT_PATH):
        dirs[:] = [d for d in dirs if d not in ["node_modules", "venv", "__pycache__", "_debug"]]
        for file in files:
            result.append(os.path.join(root, file))
    return result