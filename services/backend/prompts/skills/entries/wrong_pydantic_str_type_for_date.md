# wrong_pydantic_str_type_for_date

## Symptôme
```
ResponseValidationError: 1 validation error:
{'type': 'string_type', 'loc': ('response', ..., '<field>'), 'msg': 'Input should be a valid string', 'input': datetime.date(2024, 1, 1)}
```

Pydantic reçoit un vrai `datetime.date` (venant de la BDD) mais son schéma dit que le champ doit être une string.

## Contexte
Le schéma Pydantic type le champ en `str`, mais la colonne SQLAlchemy correspondante est un `Date` (ou `DateTime`). Quand la route lit la BDD et renvoie l'objet, la sérialisation échoue.

Comme `sqlite_date_type_mismatch`, c'est souvent la conséquence d'un fix mal fait sur le bug de shadowing (`none_required`).

## Cause profonde
Divergence de type entre le schéma Pydantic et le modèle SQLAlchemy pour un même champ. Pydantic exige `str`, la BDD fournit `date`.

## Fix correct
Ouvrir `app/schemas/<entity>.py`. Rétablir le type correct :
```python
date: Optional[date] = None
```
(ou `datetime.date` qualifié — voir `none_required_shadowing` pour éviter le shadowing).

Si l'ancienne « correction » avait ajouté `str` sur plusieurs champs de type date, corriger TOUS les champs concernés.

## Anti-fixes (INTERDIT)
- **NE PAS changer la colonne SQLAlchemy en `String`** — la BDD doit garder son type date.
- **NE PAS ajouter un `field_serializer` qui convertit en string** — c'est un patch qui masque le vrai bug.
- **NE PAS toucher au test** — le test envoie et attend une date, c'est correct.

## Comment confirmer que c'est bien ce cas
- Le message contient-il `'type': 'string_type'` avec un `input: datetime.date(...)` ?
- Le champ concerné est-il typé `str` dans le schéma mais `Date`/`DateTime` dans le modèle ?

Si oui aux deux, c'est ce bug.

## Métadonnées
- Ajouté le : entrée initiale
- Rencontré la première fois dans : cascade de mauvaises corrections après `none_required_shadowing`
- Note : compagnon fréquent de `sqlite_date_type_mismatch` — souvent le même run les produit tous les deux.
