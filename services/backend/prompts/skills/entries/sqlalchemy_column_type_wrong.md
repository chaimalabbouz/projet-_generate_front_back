# sqlalchemy_column_type_wrong

## Symptôme
```
sqlalchemy.exc.CompileError: ...
```
ou
```
sqlalchemy.exc.ArgumentError: Column type not recognized: ...
```
ou une erreur au démarrage lors de `Base.metadata.create_all()`.

## Contexte
Un type SQLAlchemy est mal utilisé dans une colonne :
- Type inexistant (`Column(Char, ...)` alors que ça n'existe pas — c'est `String`).
- Type importé mais mal appliqué (`Column(datetime, ...)` au lieu de `Column(DateTime, ...)`).
- Import manquant (voir `missing_import`).

## Cause profonde
Confusion entre les types Python (`str`, `int`, `datetime.datetime`) et les types SQLAlchemy (`String`, `Integer`, `DateTime`). Le LLM du backend agent mélange parfois les deux.

## Fix correct
Ouvrir `app/models/<entity>.py`. Table des correspondances SQLAlchemy standards :

| Type spec (dans la task_queue) | Type SQLAlchemy |
|---|---|
| `string`, `str` | `String` (ou `Text` pour du long) |
| `int`, `integer` | `Integer` |
| `bool`, `boolean` | `Boolean` |
| `float`, `numeric` | `Float` (ou `Numeric` avec précision) |
| `date` | `Date` |
| `datetime`, `timestamp` | `DateTime` |
| `time` | `Time` |
| `uuid` | `UUID(as_uuid=True)` — nécessite `from sqlalchemy.dialects.postgresql import UUID` |

Import en tête de fichier :
```python
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, Text, ForeignKey
```

## Anti-fixes (INTERDIT)
- **NE PAS utiliser des types Python bruts dans `Column(...)`** (`Column(str, ...)` est incorrect — c'est `Column(String, ...)`).
- **NE PAS créer une colonne `PickleType` ou `JSON` "pour être flexible"** — respecter la spec.

## Comment confirmer que c'est bien ce cas
L'erreur mentionne `CompileError` ou `ArgumentError` avec référence à un type de colonne.

## Métadonnées
- Ajouté le : entrée initiale
- Note : souvent combiné avec `missing_import` (le type SQL est correct mais pas importé).
