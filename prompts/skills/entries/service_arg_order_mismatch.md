# service_arg_order_mismatch

## Symptôme
Toujours un `AttributeError` où un argument reçoit un objet du mauvais type. Formes typiques :
```
AttributeError: 'Session' object has no attribute 'model_dump'
AttributeError: 'int' object has no attribute 'query'
AttributeError: 'Session' object has no attribute '<n'importe quel champ Pydantic>'
```

Le traceback pointe vers une ligne du service (ex : `db_obj = Model(**data.model_dump())` ou `db.query(Model)...`), mais la fonction service prise ISOLÉMENT paraît parfaitement correcte.

## Contexte
La route et le service utilisent des paramètres nommés dans un ordre différent. La route appelle le service avec les arguments dans le mauvais ordre positionnel, donc un objet arrive à la place d'un autre.

Exemple canonique :
```python
# route
return subscribe_to_newsletter_service(db, newsletter_create)   # ORDRE INVERSÉ

# service (attend l'ordre inverse)
def subscribe_to_newsletter(newsletter_data: NewsletterCreate, db: Session): ...
```

Résultat : `db` (Session) atterrit dans `newsletter_data`, et vice-versa. L'exception explose sur la première méthode appelée sur l'objet mal typé.

## Cause profonde
Le backend agent (LLM) génère la route et le service dans deux appels séparés. Il n'y a aucune garantie que les signatures soient cohérentes entre les deux fichiers. Le traceback pointe vers l'endroit où l'exception est LEVÉE (le service), pas où le bug a été INTRODUIT (l'appel dans la route).

C'est un bug de cohérence inter-fichiers, pas un bug local.

## Fix correct
**Toujours corriger la ROUTE, jamais le service.** La convention du projet est :

    def create_X(db: Session, x_data: XCreate)      ← db en PREMIER
    def get_X_by_id(db: Session, x_id: int)          ← db en PREMIER
    def update_X(db: Session, x_id: int, x_data)    ← db en PREMIER

Donc l'appel dans la route doit ALSO commencer par `db` :

    return create_X_service(db, payload)             ← db en PREMIER
    return get_X_by_id_service(db, id)               ← db en PREMIER

Si le service a été généré autrement (par ex. `def create_X(x_data, db)`),
il est incorrect selon la spec du projet. Regénérer le service si nécessaire
pour qu'il respecte la convention `db first`. Puis aligner la route.

Exemple concret de correction :

    # AVANT (buggé) :
    return subscribe_to_newsletter_service(newsletter_create, db)

    # APRÈS (fixé) :
    return subscribe_to_newsletter_service(db, newsletter_create)

## Anti-fixes (INTERDIT)
- **NE PAS modifier la signature du service** — la signature du service est authoritative (elle vient de la spec). Modifier le service casserait le contrat.
- **NE PAS ajouter des `keyword arguments` dans la route pour "forcer" le mapping** (ex : `service(db=db, data=data)`) sans corriger l'ordre — ça marche mais masque le vrai bug et l'entrée du skills ne s'applique plus proprement.
- **NE PAS modifier le schéma Pydantic** — le schéma est correct, ce n'est pas lui qui reçoit un mauvais type.
- **NE PAS modifier le modèle SQLAlchemy** — même raison.
- **NE PAS toucher au test** — le test est correct, il détecte un vrai bug.

## Comment confirmer que c'est bien ce cas
1. L'erreur est-elle un `AttributeError` où un objet reçoit une méthode qui n'existe pas sur son type ? (`'Session' object has no attribute '<X>'` ou `'int' object has no attribute '<X>'`)
2. En lisant le service seul, tout paraît normal ?
3. En lisant la route, l'appel `service(...)` a-t-il ses arguments dans un ordre différent de la signature `def service(...)` ?

Si oui aux trois, c'est ce bug.

## Métadonnées
- Ajouté le : entrée initiale
- Rencontré la première fois dans : entités Blog, Consultation, Newsletter (Newsletter épuisé les retries du fixer)
- Note : le fixer réussit parfois à corriger ce bug, parfois non — sans skills, le résultat était aléatoire.
