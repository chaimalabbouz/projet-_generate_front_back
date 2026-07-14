# circular_import

## Symptôme
```
ImportError: cannot import name '<X>' from partially initialized module '<module>' (most likely due to a circular import)
```

## Contexte
Deux fichiers s'importent mutuellement. Souvent modèle ↔ schéma quand les type hints utilisent l'autre :
```python
# app/models/blog.py
from app.schemas.blog import BlogCreate    # ← référence croisée

# app/schemas/blog.py
from app.models.blog import Blog           # ← référence croisée
```

## Cause profonde
Python charge les modules à la volée. Si A importe B pendant que B est en train d'importer A, Python fournit un module A partiellement chargé — d'où « partially initialized module ».

## Fix correct
Casser la boucle. Trois techniques, par ordre de préférence :

**1. Supprimer l'import qui ne sert à rien (le plus fréquent).**
Un modèle SQLAlchemy n'a JAMAIS besoin d'importer un schéma Pydantic. Un schéma Pydantic n'a JAMAIS besoin d'importer un modèle SQLAlchemy. Supprimer l'import fautif.

**2. Utiliser une string forward-ref pour l'annotation.**
```python
def create_blog(data: "BlogCreate") -> "Blog":    # entre guillemets
```
Le type n'est pas résolu à l'import, plus de cycle.

**3. Déplacer l'import à l'intérieur de la fonction** (dernier recours).
```python
def foo():
    from app.models.blog import Blog
    ...
```

## Anti-fixes (INTERDIT)
- **NE PAS créer un troisième fichier "commun" juste pour casser le cycle** si une des autres solutions suffit.
- **NE PAS commenter l'import sans remplacer** — le nom manquera à l'exécution (voir `missing_import`).

## Comment confirmer que c'est bien ce cas
L'erreur mentionne littéralement `circular import` ou `partially initialized module`.

## Métadonnées
- Ajouté le : entrée initiale
- Note : rare si le générateur suit les conventions (modèles n'importent pas les schémas, et inversement).
