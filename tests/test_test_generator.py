"""Le TestGenerator est déterministe : on peut le tester sans LLM."""
from services.backend.agents.test_generator import TestGenerator

TASK_QUEUE = [
    {
        "order": 1, "entity": "Doctor", "file": "app/models/doctor.py",
        "type": "model", "status": "pending",
        "fields": [
            {"name": "id", "type": "Integer", "primary_key": True},
            {"name": "name", "type": "String", "nullable": False},
        ],
    },
    {
        "order": 2, "entity": "Doctor", "file": "app/schemas/doctor.py",
        "type": "schema", "status": "pending",
        "schemas": [{"name": "DoctorCreate", "fields": [{"name": "name", "type": "str"}]}],
    },
    {
        "order": 3, "entity": "Doctor", "file": "app/routes/doctor.py",
        "type": "route", "status": "pending", "test_status": "pending",
        "functions": [
            {"method": "POST", "path": "/doctors",
             "operationId": "create_doctor", "status_code": 201},
        ],
    },
]


def test_generates_valid_python():
    code = TestGenerator(TASK_QUEUE, {"Doctor": []}).generate("Doctor")
    compile(code, "test_doctor.py", "exec")   # doit compiler


def test_uses_status_code_from_plan():
    code = TestGenerator(TASK_QUEUE, {"Doctor": []}).generate("Doctor")
    assert "assert response.status_code == 201" in code
    assert "def test_create_doctor():" in code


def test_is_deterministic():
    gen = TestGenerator(TASK_QUEUE, {"Doctor": []})
    assert gen.generate("Doctor") == gen.generate("Doctor")