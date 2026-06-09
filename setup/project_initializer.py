import os
import subprocess
import sys
from orchestrator.state import GraphState

# =========================
# PATHS
# =========================
GENERATED_PROJECT_PATH = "C:/Users/binitns/Desktop/generated_project"

FOLDERS = [
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

DEPENDENCIES = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pydantic",
    "pytest",
    "httpx",
    "pytest-asyncio",
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

# =========================
# MAIN FUNCTION (LANGGRAPH NODE)
# =========================
def initialize_project(state: GraphState) -> GraphState:
    try:
        _create_folders()
        _create_init_files()
        _create_venv()
        _install_dependencies()
        _create_database_file()
        _create_requirements_file()

        state.workflow_state = "setup_done"
        state.filesystem_state = _list_files()

    except Exception as e:
        state.workflow_state = "setup_failed"
        state.error_log = (state.error_log or "") + f"\n[SETUP ERROR] {str(e)}"

    return state

# =========================
# STEPS
# =========================
def _create_folders():
    print("[SETUP] Creating folders...")
    for folder in FOLDERS:
        full_path = os.path.join(GENERATED_PROJECT_PATH, folder)
        os.makedirs(full_path, exist_ok=True)
        print(f"  ✓ {full_path}")


def _create_init_files():
    print("[SETUP] Creating __init__.py files...")
    for init_file in INIT_FILES:
        full_path = os.path.join(GENERATED_PROJECT_PATH, init_file)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("")
        print(f"  ✓ {full_path}")


def _create_venv():
    print("[SETUP] Creating virtual environment...")
    venv_path = os.path.join(GENERATED_PROJECT_PATH, "venv")
    subprocess.run(
        [sys.executable, "-m", "venv", venv_path],
        check=True
    )
    print(f"  ✓ venv created at {venv_path}")


def _install_dependencies():
    print("[SETUP] Installing dependencies...")

    if os.name == "nt":
        pip_path = os.path.join(GENERATED_PROJECT_PATH, "venv", "Scripts", "pip")
    else:
        pip_path = os.path.join(GENERATED_PROJECT_PATH, "venv", "bin", "pip")

    subprocess.run(
        [pip_path, "install"] + DEPENDENCIES,
        check=True
    )
    print(f"  ✓ Dependencies installed: {', '.join(DEPENDENCIES)}")


def _create_database_file():
    print("[SETUP] Creating database.py...")
    full_path = os.path.join(GENERATED_PROJECT_PATH, "app", "database.py")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(DATABASE_PY)
    print(f"  ✓ {full_path}")


def _create_requirements_file():
    print("[SETUP] Creating requirements.txt...")
    full_path = os.path.join(GENERATED_PROJECT_PATH, "requirements.txt")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(REQUIREMENTS_TXT)
    print(f"  ✓ {full_path}")


def _list_files() -> list:
    result = []
    for root, dirs, files in os.walk(GENERATED_PROJECT_PATH):
        for file in files:
            full_path = os.path.join(root, file)
            result.append(full_path)
    return result