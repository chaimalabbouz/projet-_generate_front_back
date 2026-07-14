# pydantic_orm_mode_missing

## Symptôme
Deux formes possibles :
- `ResponseValidationError` sur un endpoint qui retourne un objet SQLAlchemy directement, avec des messages du type "Input should be a valid dictionary" ou champs manquants.
- La réponse HTTP est vide, ou ne contient que certains champs, alors que la BDD contient bien les données.

## Contexte
Le schéma Pydantic de réponse (`class Blog(BaseModel)` ou `class BlogResponse(BaseModel)`) n'a pas la configuration qui autorise Pydantic à lire des attributs d'objet (au lieu de clés de dictionnaire). Sans ça, Pydantic n'arrive pas à sérialiser un objet SQLAlchemy renvoyé par une route.

## Cause profonde
Pydantic v1 attend par défaut un dictionnaire en entrée. Un objet SQLAlchemy expose ses champs comme attributs, pas comme items de dictionnaire.

- Pydantic v1 : il faut activer `class Config: orm_mode = True`.
- Pydantic v2 : il faut activer `model_config = ConfigDict(from_attributes=True)`.

Sans cela, la sérialisation depuis un objet ORM échoue silencieusement ou bruyamment.

## Fix correct
Ouvrir `app/schemas/<entity>.py`. Dans la classe de réponse (celle utilisée comme `response_model` par la route), ajouter :

**Pydantic v2 (recommandé) :**
```python
from pydantic import BaseModel, ConfigDict

class Blog(BaseModel):
    id: int
    title: str
    # ... autres champs

    model_config = ConfigDict(from_attributes=True)
```

**Pydantic v1 (si le projet est encore en v1) :**
```python
class Blog(BaseModel):
    id: int
    # ...

    class Config:
        orm_mode = True
```

Vérifier avec `pip show pydantic` quelle version est utilisée. Ne pas mélanger les deux syntaxes (voir `pydantic_v1_v2_mixup`).

## Anti-fixes (INTERDIT)
- **NE PAS convertir manuellement l'objet SQLAlchemy en dict dans la route** (`Blog(**{...})`) — c'est du code redondant et fragile.
- **NE PAS retirer le `response_model`** de la route pour "faire passer" — on perd la validation et la doc OpenAPI.
- **NE PAS créer une deuxième classe de conversion** — la solution tient en une ligne de config.

## Comment confirmer que c'est bien ce cas
La route retourne-t-elle directement un objet SQLAlchemy (`return db_blog`) sans le convertir explicitement en dict, et le schéma de réponse manque-t-il `from_attributes=True` ou `orm_mode = True` ?

## Métadonnées
- Ajouté le : entrée initiale
- Note : bug fréquent quand le backend agent oublie la config, ou quand il mélange v1/v2 (voir `pydantic_v1_v2_mixup`).
