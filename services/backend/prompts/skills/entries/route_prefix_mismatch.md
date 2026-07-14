# route_prefix_mismatch

## Symptôme
```
assert 404 == 200    # ou 404 == 201
```
Le test tape une URL mais reçoit `404 Not Found` alors que l'endpoint est censé exister.

## Contexte
Le chemin utilisé par le test ne correspond pas au path déclaré dans la route. Cas fréquents :
- Test tape `/blogs` mais la route est `/blog` (singulier vs pluriel).
- Test tape `/blog/1` mais la route est `/blog/{blog_id}` avec un nom de paramètre différent (peu impact) ou un slash de trop.
- Router monté avec un `prefix=...` qui décale toutes les URLs.

## Cause profonde
Divergence entre le path déclaré dans le décorateur de la route et celui construit par le test. La source de vérité est **la spec (task_queue → `functions[].path`)** que le TestGenerator utilise pour générer le test.

## Fix correct
Ouvrir `app/routes/<entity>.py`. Vérifier le décorateur :
```python
@router.post("/blog", ...)         # doit matcher le path de la spec
@router.get("/blog", ...)
@router.get("/blog/{id}", ...)
```

Aligner sur la spec fournie dans le contexte du fixer. Si la spec dit `/blog`, la route doit être `/blog`, pas `/blogs`.

Vérifier aussi `app/main.py` : si le router est monté avec `app.include_router(router, prefix="/api")`, toutes les routes sont préfixées par `/api`. Le test attend-il ce préfixe ?

## Anti-fixes (INTERDIT)
- **NE PAS modifier le test** pour taper une autre URL.
- **NE PAS ajouter une redirection** (`@router.get("/blogs")` qui redirige vers `/blog`) — c'est un patch fragile.

## Comment confirmer que c'est bien ce cas
Le code observé est `404`, et la comparaison entre le path déclaré dans la route et l'URL construite par le test montre une différence (singulier/pluriel, préfixe, nom de paramètre dans le chemin).

## Métadonnées
- Ajouté le : entrée initiale
- Note : la spec est authoritative — toujours corriger le code d'application pour qu'il matche la spec, jamais l'inverse.
