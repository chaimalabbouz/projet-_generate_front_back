from agents.seed_generator import SeedGenerator

# --- mini task_queue d'exemple (juste pour tester le LLM) ---
task_queue = [
    {
        "type": "model",
        "entity": "Doctor",
        "file": "app/models/doctor.py",
        "fields": [
            {"name": "id", "type": "Integer", "primary_key": True},
            {"name": "name", "type": "String(255)"},
            {"name": "specialty", "type": "String(255)"},
            {"name": "biography", "type": "Text"},
            {"name": "image_url", "type": "String(255)"},
            {"name": "email", "type": "String(255)"},
        ],
    },
    {
        "type": "model",
        "entity": "Blog",
        "file": "app/models/blog.py",
        "fields": [
            {"name": "id", "type": "Integer", "primary_key": True},
            {"name": "title", "type": "String(255)"},
            {"name": "content", "type": "Text"},
            {"name": "author_name", "type": "String(255)"},
        ],
    },
]

gen = SeedGenerator(task_queue, dependency_graph={}, rows_per_entity=5)
code = gen.generate()

print(code)  # affiche le seed.py généré