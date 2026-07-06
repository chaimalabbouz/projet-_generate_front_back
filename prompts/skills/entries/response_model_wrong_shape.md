# response_model_wrong_shape

## Symptôme
`ResponseValidationError` avec un `loc` qui révèle une mauvaise forme :
- `loc: ('response', 0, ...)` sur un endpoint qui devrait renvoyer un objet unique (le 0 indique que Pydantic essaie d'itérer).
- `loc: ('response', ...)` sur un endpoint qui devrait renvoyer une liste (pas de 0).

## Contexte
Le décorateur de la route déclare le mauvais type dans `response_model` :
- `response_model=Blog` alors que la route retourne une liste.
- `response_model=List[Blog]` alors que la route retourne un seul objet.

## Cause profonde
Divergence entre le type déclaré et le type effectivement retourné par la fonction. FastAPI valide la réponse contre le `response_model`, et la validation échoue avec un `loc` qui trahit la mauvaise forme.

## Fix correct
Ouvrir `app/routes/<entity>.py`. Aligner `response_model` avec ce que retourne le service :

**Endpoint list (retourne une liste) :**
```python
@router.get("/blog", response_model=List[Blog])
def list_blog_posts(...):
    return list_blog_posts_service(db)   # renvoie List[Blog]
```

**Endpoint single (retourne un objet) :**
```python
@router.get("/blog/{id}", response_model=Blog)
def get_blog_post_by_id(...):
    return get_blog_post_by_id_service(id, db)   # renvoie un seul Blog
```

Vérifier que `List` est bien importé depuis `typing`.

## Anti-fixes (INTERDIT)
- **NE PAS retirer le `response_model`** — on perd la validation et la doc OpenAPI.
- **NE PAS modifier le service** pour qu'il retourne autre chose — le service est correct, c'est la déclaration de la route qui ment.

## Comment confirmer que c'est bien ce cas
Le `loc` du message d'erreur contient-il `('response', 0, ...)` alors que la route est censée retourner un objet unique ? Ou l'inverse ?

## Métadonnées
- Ajouté le : entrée initiale
- Note : bug de forme, pas de contenu — les champs individuels sont corrects, c'est la structure globale qui est fausse.
