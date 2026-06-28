import os
import shutil
import subprocess
import sys
from orchestrator.state import GraphState

# =========================
# PATHS
# =========================
GENERATED_PROJECT_PATH = "C:/Users/binitns/Desktop/generated_project"
FRONTEND_PATH = os.path.join(GENERATED_PROJECT_PATH, "frontend")
INPUTS_FRONTEND_PATH = "inputs/code_front"

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

BACKEND_DEPENDENCIES = [
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

API_CONFIG_TS = """const API_BASE_URL = "http://localhost:8000";

export default API_BASE_URL;
"""

# =========================
# MAIN FUNCTION (LANGGRAPH NODE)
# =========================
def initialize_project(state: GraphState) -> GraphState:
    try:
        # ── BACKEND ──
        _create_backend_folders()
        _create_init_files()
        _create_venv()
        _install_backend_dependencies()
        _create_database_file()
        _create_requirements_file()

        

        state.workflow_state = "setup_done"
        state.filesystem_state = _list_files()

    except Exception as e:
        state.workflow_state = "setup_failed"
        state.error_log = (state.error_log or "") + f"\n[SETUP ERROR] {str(e)}"

    return state

# =========================
# BACKEND STEPS
# =========================
def _create_backend_folders():
    print("[SETUP] Creating backend folders...")
    for folder in BACKEND_FOLDERS:
        full_path = os.path.join(GENERATED_PROJECT_PATH, folder)
        os.makedirs(full_path, exist_ok=True)
        print(f"  ✓ {full_path}")


def _create_init_files():
    #print("[SETUP] Creating __init__.py files...")
    for init_file in INIT_FILES:
        full_path = os.path.join(GENERATED_PROJECT_PATH, init_file)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("")
        #print(f"  ✓ {full_path}")


def _create_venv():
    #print("[SETUP] Creating backend virtual environment...")
    venv_path = os.path.join(GENERATED_PROJECT_PATH, "venv")
    subprocess.run(
        [sys.executable, "-m", "venv", venv_path],
        check=True
    )
    #print(f"  ✓ venv created at {venv_path}")


def _install_backend_dependencies():
    #print("[SETUP] Installing backend dependencies...")
    if os.name == "nt":
        pip_path = os.path.join(GENERATED_PROJECT_PATH, "venv", "Scripts", "pip")
    else:
        pip_path = os.path.join(GENERATED_PROJECT_PATH, "venv", "bin", "pip")

    subprocess.run(
        [pip_path, "install"] + BACKEND_DEPENDENCIES,
        check=True
    )
    #print(f"  ✓ Backend dependencies installed")


def _create_database_file():
    #print("[SETUP] Creating database.py...")
    full_path = os.path.join(GENERATED_PROJECT_PATH, "app", "database.py")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(DATABASE_PY)
    #print(f"  ✓ {full_path}")


def _create_requirements_file():
    #print("[SETUP] Creating requirements.txt...")
    full_path = os.path.join(GENERATED_PROJECT_PATH, "requirements.txt")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(REQUIREMENTS_TXT)
    #print(f"  ✓ {full_path}")


# =========================
# FRONTEND STEPS
# =========================
def _create_vite_project():
    #print("[SETUP] Creating Vite React project...")
    os.makedirs(GENERATED_PROJECT_PATH, exist_ok=True)

    subprocess.run(
        ["npm", "create", "vite@latest", "frontend", "--", "--template", "react-ts"],
        cwd=GENERATED_PROJECT_PATH,
        check=True,
        shell=True
    )
    #print(f"  ✓ Vite project created at {FRONTEND_PATH}")


def _install_frontend_dependencies():
    print("[SETUP] Installing frontend dependencies...")
    subprocess.run(
        ["npm", "install"],
        cwd=FRONTEND_PATH,
        check=True,
        shell=True
    )
    #print(f"  ✓ Frontend dependencies installed")


def _copy_frontend_files():
    #print("[SETUP] Copying frontend files...")

    components_src = os.path.join(INPUTS_FRONTEND_PATH, "components")
    components_dst = os.path.join(FRONTEND_PATH, "src", "components")
    os.makedirs(components_dst, exist_ok=True)

    if os.path.exists(components_src):
        for file in os.listdir(components_src):
            shutil.copy2(
                os.path.join(components_src, file),
                os.path.join(components_dst, file)
            )
            #print(f"  ✓ Copied component: {file}")

    pages_src = os.path.join(INPUTS_FRONTEND_PATH, "pages")
    pages_dst = os.path.join(FRONTEND_PATH, "src", "pages")
    os.makedirs(pages_dst, exist_ok=True)

    if os.path.exists(pages_src):
        for file in os.listdir(pages_src):
            shutil.copy2(
                os.path.join(pages_src, file),
                os.path.join(pages_dst, file)
            )
            #print(f"  ✓ Copied page: {file}")


def _create_api_config():
    #print("[SETUP] Creating API config...")
    config_dir = os.path.join(FRONTEND_PATH, "src", "config")
    os.makedirs(config_dir, exist_ok=True)
    full_path = os.path.join(config_dir, "api.ts")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(API_CONFIG_TS)
    print(f"  ✓ {full_path}")


# =========================
# UTILS
# =========================
def _list_files() -> list:
    result = []
    for root, dirs, files in os.walk(GENERATED_PROJECT_PATH):
        dirs[:] = [d for d in dirs if d not in ["node_modules", "venv", "__pycache__"]]
        for file in files:
            full_path = os.path.join(root, file)
            result.append(full_path)
    return result