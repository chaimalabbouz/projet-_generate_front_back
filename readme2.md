🧠 🟣 Orchestrator Agent
reçoit la demande utilisateur
gère le workflow global
décide quel agent appeler
garde l’état du projet
lance test → fix → retry
📄 🟡 OpenAPI Agent
transforme texte → OpenAPI spec
définit endpoints, models, requests, responses
🧾 🟣 Planner Agent
lit OpenAPI
découpe en entités (User, Product…)
génère structure projet :
folders
files
définit :
ordre de génération
dépendances entre entités
associe chaque endpoint à un fichier
🧑‍💻 🔵 Backend Generator Agent
reçoit 1 entité à la fois
génère code :
model
service
controller
routes
utilise OpenAPI + plan
évite hallucination en suivant spec
🧪 🟠 Tester Agent
lance Docker
teste API endpoints
vérifie :
serveur démarre
routes fonctionnent
JSON correct
retourne logs + erreurs
🔧 🔴 Fixer Agent
analyse erreurs + logs
modifie code backend
renvoie version corrigée
relance cycle test
🎨 🟢 Frontend Generator Agent
input : OpenAPI + Figma JSON
génère pages (3–5 pages)
crée composants React/Vue
🔗 🟣 API-Linker Agent
connecte frontend ↔ backend
utilise OpenAPI comme contrat
évite mauvais endpoints
corrige payloads + requests
🔁 FLOW GLOBAL
User input
→ OpenAPI Agent
→ Planner Agent
→ Backend Generator (par entité)
→ Tester Agent
→ Fixer Agent (loop)
→ Frontend Generator
→ API-Linker Agent
→ Frontend test (optionnel)
------------------------------------------------------------------------------------
------------------------------------------------------------------------------------
state 
🧠 📦 STATE GLOBAL (version simple)
📝 1. user_input
description du projet donnée par l’utilisateur

👉 pourquoi : point de départ du système

📄 2. openapi_spec
spec OpenAPI générée

👉 pourquoi : contrat central backend/frontend

🗺️ 3. plan
liste des entités
structure des dossiers
liste des fichiers à créer
ordre de génération

👉 pourquoi : guide tous les agents backend

📌 4. task_queue
liste des tâches à exécuter
ex : “generate ProductService.js”

👉 pourquoi : permet exécution step-by-step

🧪 5. test_status
succès / échec des tests
logs Docker / API errors

👉 pourquoi : feedback pour correction

🔧 6. fix_status (ou last_error)
dernière erreur détectée
correction appliquée

👉 pourquoi : boucle debug propre

🎨 7. frontend_spec
JSON Figma ou description UI

👉 pourquoi : base du frontend generator

🔁 8. workflow_state
running / testing / fixing / done
étape actuelle du système

👉 pourquoi : contrôle global du pipeline