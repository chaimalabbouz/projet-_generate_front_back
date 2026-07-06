# missing_import

## Symptôme
```
NameError: name '<X>' is not defined
```
Où `<X>` est typiquement : `Optional`, `List`, `Dict`, `Union`, `date`, `datetime`, `UUID`, `HTTPException`, `Depends`, `Session`, un nom de modèle, etc.

## Contexte
Un nom (type, classe, fonction) est utilisé dans le fichier mais son import est absent en tête de fichier. Se produit surtout après un fix précédent qui a ajouté une annotation sans ajouter l'import correspondant.

## Cause profonde
Le LLM qui a généré ou modifié le fichier a ajouté une annotation ou un appel sans mettre à jour la section imports. Bug purement mécanique.

## Fix correct
Ouvrir le fichier concerné (`app/models/`, `app/schemas/`, `app/services/`, ou `app/routes/`). Identifier le nom manquant. Ajouter l'import approprié.

Table de correspondance rapide :

| Nom manquant | Import à ajouter |
|---|---|
| `Optional`, `List`, `Dict`, `Union`, `Any`, `Tuple` | `from typing import Optional, List, Dict, Union, Any, Tuple` |
| `date`, `datetime`, `time`, `timedelta` | `from datetime import date, datetime, time, timedelta` |
| `UUID` | `from uuid import UUID` |
| `BaseModel`, `Field`, `ConfigDict` | `from pydantic import BaseModel, Field, ConfigDict` |
| `Session` | `from sqlalchemy.orm import Session` |
| `Column`, `Integer`, `String`, `Date`, `DateTime`, `ForeignKey`, `Boolean` | `from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean` |
| `Base` | `from app.database import Base` |
| `get_db` | `from app.database import get_db` |
| `APIRouter`, `Depends`, `HTTPException` | `from fastapi import APIRouter, Depends, HTTPException` |
| Nom d'un modèle SQLAlchemy | `from app.models.<entity> import <ModelName>` |
| Nom d'un schéma Pydantic | `from app.schemas.<entity> import <SchemaName>` |

## Anti-fixes (INTERDIT)
- **NE PAS remplacer le type par une chaîne de caractères** (`"Optional[int]"` en string forward-ref) sauf si c'est nécessaire pour casser un import circulaire — dans ce cas, voir `circular_import`.
- **NE PAS supprimer l'annotation qui utilise le nom manquant** — l'annotation est correcte, c'est l'import qui manque.
- **NE PAS toucher au test.**

## Comment confirmer que c'est bien ce cas
L'erreur est un simple `NameError: name '<X>' is not defined`. C'est presque toujours ce cas.

## Métadonnées
- Ajouté le : entrée initiale
- Note : bug très fréquent après une correction LLM, car les LLMs oublient souvent d'ajuster les imports.
