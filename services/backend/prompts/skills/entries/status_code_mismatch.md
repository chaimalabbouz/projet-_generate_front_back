# status_code_mismatch

## Symptôme
```
assert 422 == 201    # ou 200 == 204, 200 == 201, etc.
```

Le test attend un status code précis, mais la route en renvoie un autre.

## Contexte
Deux causes principales à distinguer :

**Cas A — Le décorateur de route déclare le mauvais code.** Ex : `@router.post("/blog", status_code=200)` alors que le test attend 201.

**Cas B — Le payload envoyé par le test échoue la validation Pydantic** (d'où 422 Unprocessable Entity). C'est un symptôme d'UN AUTRE bug (souvent `none_required_shadowing`, `missing_import`, ou un champ obligatoire manquant dans le payload).

## Cause profonde
- **Cas A** : divergence entre la spec (qui définit les status codes attendus) et le décorateur généré.
- **Cas B** : le status 422 vient toujours de Pydantic qui rejette le payload. Le vrai bug est ailleurs — c'est la validation d'entrée qui a un problème, pas le status code lui-même.

## Fix correct

**Cas A — Aligner le décorateur avec ce que le test attend :**
```python
@router.post("/blog", response_model=Blog, status_code=201)   # 201 pour POST create
@router.delete("/blog/{id}", status_code=204)                 # 204 pour DELETE
@router.get("/blog", response_model=List[Blog])               # 200 par défaut, pas besoin
@router.put("/blog/{id}", response_model=Blog, status_code=200)   # 200 pour update
```

**Cas B — Si le code observé est 422 :**
Ne PAS toucher au status code. Lire le corps de la réponse 422 pour voir quelle validation a échoué. Puis chercher dans l'index l'entrée correspondant à cette validation :
- Si `none_required` → entrée `none_required_shadowing`.
- Si `missing` → il manque un champ obligatoire dans le payload (bug dans le générateur de test ou dans le schéma).
- Si `string_type` avec input `date` → entrée `wrong_pydantic_str_type_for_date`.

## Anti-fixes (INTERDIT)
- **NE PAS changer le status code dans le décorateur pour matcher ce que le test reçoit** (ex : passer à 422 pour faire disparaître l'erreur). C'est masquer le bug, pas le résoudre.
- **NE PAS modifier le test** pour attendre un autre code.
- **NE PAS ajouter un try/except qui renvoie le bon code artificiellement.**

## Comment confirmer que c'est bien ce cas
Regarder le code observé :
- **422** → cas B, il y a un bug de validation Pydantic en amont, chercher ailleurs.
- **200/201/204 vs autre** → cas A, aligner le décorateur.

## Métadonnées
- Ajouté le : entrée initiale
- Note : le 422 est le piège classique — beaucoup de fixers changent le status code pour faire taire l'erreur alors que le vrai bug est un autre.
