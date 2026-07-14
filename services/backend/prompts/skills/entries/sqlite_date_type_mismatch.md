# sqlite_date_type_mismatch

## Symptôme
```
TypeError: SQLite Date type only accepts Python date objects as input.
[SQL: INSERT INTO <table> (..., date, ...) VALUES (...)]
[parameters: [{'date': 'test_string', ...}]]
```

Le paramètre passé à SQLAlchemy pour une colonne `Date` est une chaîne de caractères, pas un objet `date`.

## Contexte
Se produit après qu'un fix précédent a incorrectement changé le type d'un champ Pydantic. Typiquement : le champ était `Optional[date]`, un fixer a paniqué face au bug de shadowing (`none_required`) et a « corrigé » en typant le champ `str`. Pydantic laisse alors passer la string du test (`"test_string"` ou `"2024-01-01"` non parsée), qui arrive telle quelle jusqu'à la couche SQLAlchemy.

C'est presque toujours la conséquence d'un fix mal fait sur `none_required_shadowing`.

## Cause profonde
Le schéma Pydantic et le modèle SQLAlchemy ne s'accordent plus sur le type. Pydantic est trop permissif (accepte `str`), SQLAlchemy est strict (`Date` exige un `datetime.date`).

Le champ Pydantic aurait dû rester `Optional[date]`. Le vrai bug initial (shadowing) devait être fixé autrement (voir `none_required_shadowing`), pas en changeant le type.

## Fix correct
**Étape 1 — Rétablir le type correct dans le schéma Pydantic.** Ouvrir `app/schemas/<entity>.py`. Rétablir le champ à son type d'origine :
```python
date: Optional[date] = None    # ou datetime.date, voir étape 2
```

**Étape 2 — Corriger le bug de shadowing sous-jacent, PAS en changeant le type.** Ajouter en toute première ligne du fichier :
```python
from __future__ import annotations
```
OU utiliser un type qualifié :
```python
import datetime
# ...
    date: Optional[datetime.date] = None
```

Voir l'entrée `none_required_shadowing` pour l'explication complète du bug qui a poussé quelqu'un à faire cette « correction » erronée.

## Anti-fixes (INTERDIT)
- **NE PAS changer la colonne SQLAlchemy en `String`** — la spec dit que c'est une date, la BDD doit stocker une date.
- **NE PAS parser la string dans le service** (`date.fromisoformat(data.date)`) — c'est un patch qui masque le vrai bug et complique la couche service.
- **NE PAS modifier le test pour envoyer une string à la place d'une date** — les tests sont la source de vérité.
- **NE PAS ajouter un validator Pydantic qui convertit la string** — même raison, on masque le bug au lieu de le résoudre.

## Comment confirmer que c'est bien ce cas
1. L'erreur mentionne-t-elle `SQLite Date type only accepts Python date objects` ?
2. Le champ concerné a-t-il un type `str` dans le schéma Pydantic mais `Date` dans le modèle SQLAlchemy ?

Si oui aux deux, c'est ce bug.

## Métadonnées
- Ajouté le : entrée initiale
- Rencontré la première fois dans : run où le fixer a « corrigé » `none_required_shadowing` en changeant le type
- Note : bug typique en cascade — souvent créé par une correction ratée d'un autre bug.
