# depends_get_db_missing

## Symptôme
```
AttributeError: 'function' object has no attribute 'query'
TypeError: 'Depends' object is not callable
AttributeError: 'generator' object has no attribute 'query'
```

Une opération BDD dans un service ou une route échoue parce que `db` n'est pas une vraie session.

## Contexte
La route utilise la mauvaise syntaxe pour injecter la session. Trois erreurs typiques :

```python
def create_blog_post(blog: BlogCreate, db: Session = get_db):        # ← manque Depends()
def create_blog_post(blog: BlogCreate, db = Depends(get_db())):      # ← get_db() au lieu de get_db
def create_blog_post(blog: BlogCreate, db: Session):                 # ← pas d'injection du tout
```

## Cause profonde
FastAPI n'exécute l'injection de dépendance que si le paramètre a `= Depends(...)`. Sans ça, la valeur par défaut est prise littéralement — donc `db` reçoit la fonction elle-même, ou un générateur non consommé.

## Fix correct
Ouvrir `app/routes/<entity>.py`. Vérifier chaque signature de route :
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

@router.get("/blog")
def list_blog_posts(db: Session = Depends(get_db)):    # ← syntaxe correcte
    ...
```

Points clés :
- `Depends(get_db)` — sans parenthèses après `get_db`.
- `db: Session = Depends(get_db)` — type + default.
- Imports : `Depends` depuis `fastapi`, `Session` depuis `sqlalchemy.orm`, `get_db` depuis `app.database`.

## Anti-fixes (INTERDIT)
- **NE PAS créer une session dans le service** (`db = SessionLocal()`) pour contourner — casse le cycle de vie et laisse fuir des connexions.
- **NE PAS retirer le paramètre `db`** — le service en a besoin.

## Comment confirmer que c'est bien ce cas
L'erreur mentionne un objet inattendu (`function`, `generator`, `Depends`) là où une `Session` était attendue. Vérifier la signature de la route.

## Métadonnées
- Ajouté le : entrée initiale
- Note : parfois combiné avec `missing_import` (Depends non importé).
