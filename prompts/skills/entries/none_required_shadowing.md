# none_required_shadowing

## Symptôme
```
ResponseValidationError: 1 validation error:
{'type': 'none_required', 'loc': ('response', ..., '<field>'), 'msg': 'Input should be None', 'input': <valeur réelle>}
```

Le message dit que le champ « doit être None » alors qu'il devrait clairement contenir une vraie valeur.

## Contexte
Se produit dans un schéma Pydantic quand le NOM d'un champ est identique à un TYPE Python importé dans le même fichier. Noms typiquement piégeux : `date`, `type`, `id`, `list`, `str`, `int`, `bool`, `time`, `datetime`.

Exemple canonique :
```python
from datetime import date

class Blog(BaseModel):
    date: Optional[date] = None    # ← PIÈGE INVISIBLE
```

## Cause profonde
Ce n'est PAS une erreur de logique ni de syntaxe. C'est un piège d'évaluation Python.

Dans le corps d'une classe, Python évalue **la valeur assignée AVANT de résoudre l'annotation**. Séquence exacte :

1. Python lit `date: Optional[date] = None`.
2. Il assigne d'abord `date = None` dans l'espace de noms de la classe.
3. Puis il évalue l'annotation `Optional[date]` — mais dans le namespace de la classe, `date` ne pointe plus vers le type `datetime.date`, il pointe vers le `None` qu'on vient d'assigner.
4. L'annotation devient donc `Optional[None]`, ce qui se simplifie en `NoneType`.
5. Pydantic voit un champ typé `NoneType` → il exige que ce champ soit `None`, jamais autre chose.

Résultat : le champ silencieusement transformé en « doit être None ». Le code a l'air 100% correct à l'œil nu.

## Fix correct
Ouvrir `app/schemas/<entity>.py`. Appliquer UN des deux fixes :

**Fix A (recommandé)** — Ajouter en toute première ligne du fichier :
```python
from __future__ import annotations
```
Cela diffère l'évaluation de toutes les annotations, ce qui casse le mécanisme du shadowing.

**Fix B (alternative)** — Qualifier le type explicitement. Remplacer :
```python
from datetime import date
# ...
    date: Optional[date] = None
```
par :
```python
import datetime
# ...
    date: Optional[datetime.date] = None
```
Le type qualifié `datetime.date` ne peut pas être écrasé par le nom du champ.

## Anti-fixes (INTERDIT)
- **NE PAS changer le type du champ pour `str`** — ça crée un nouveau bug (mismatch avec la colonne SQLAlchemy `Date`, cf. entrée `wrong_pydantic_str_type_for_date`).
- **NE PAS modifier le modèle SQLAlchemy** (`app/models/<entity>.py`) — le modèle est correct, le bug est uniquement dans le schéma Pydantic.
- **NE PAS renommer le champ** (`date` → `post_date`) — ça change l'API publique et casse la spec. Corriger le typage, pas le nommage.
- **NE PAS toucher au fichier de test** — les tests sont la source de vérité.
- **NE PAS supprimer `Optional`** — le champ peut légitimement être nullable, ce n'est pas la cause du bug.

## Comment confirmer que c'est bien ce cas
Deux vérifications rapides :
1. Le champ Pydantic qui pose problème a-t-il un nom identique à un type importé dans le même fichier ? Si oui, quasi certain.
2. Le message d'erreur contient-il littéralement `'type': 'none_required'` et `'msg': 'Input should be None'` ? Si oui, c'est bien ce bug.

## Métadonnées
- Ajouté le : entrée initiale
- Rencontré la première fois dans : run de génération avec entité Blog (champ `date`)
- Note : ce bug est aléatoire selon la sortie du LLM du backend agent, il peut apparaître ou non sur le même input.
