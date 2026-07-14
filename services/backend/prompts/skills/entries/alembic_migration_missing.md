# alembic_migration_missing

## Symptôme
```
sqlalchemy.exc.OperationalError: no such table: <table>
```

## Contexte
Le test tape une requête sur une table qui n'existe pas dans la BDD. Cas typiques :
- Le fichier de test ne fait pas `Base.metadata.create_all(bind=engine)` avant les tests.
- Le modèle SQLAlchemy n'est pas importé avant `create_all` — donc SQLAlchemy ne connaît pas la table.
- La fixture `setup_database` a un problème.

## Cause profonde
SQLAlchemy ne crée les tables que pour les modèles qu'il « connaît » via `Base.metadata`. Un modèle non importé au moment de `create_all()` ne sera pas créé.

## Fix correct
Dans le pipeline actuel, le `TestGenerator` fait déjà `Base.metadata.create_all(bind=engine)` dans la fixture `setup_database` et importe les modèles nécessaires en tête du fichier de test. Si l'erreur apparaît malgré tout, chercher :

1. **Modèle non importé dans le fichier de test.** Vérifier que le modèle apparaît bien dans les imports du test :
   ```python
   from app.models.<entity> import <Entity>
   ```
   S'il manque, l'ajouter (mais **ne pas modifier le test** — le vrai fix est ailleurs, dans le TestGenerator).

2. **`Base` partagée entre modèle et test.** Vérifier que `app/models/<entity>.py` importe `Base` depuis `app/database.py`, la MÊME `Base` que celle utilisée dans le test.

3. **Nom de table incorrect.** Vérifier que `__tablename__` dans le modèle correspond bien à ce que la requête attend.

## Anti-fixes (INTERDIT)
- **NE PAS créer la table manuellement en SQL brut** dans le test — hack.
- **NE PAS commenter le test** ou changer la table qu'il interroge.

## Comment confirmer que c'est bien ce cas
L'erreur mentionne `no such table: <nom>`. Vérifier l'existence et l'import du modèle.

## Métadonnées
- Ajouté le : entrée initiale
- Note : rare dans le pipeline actuel car le TestGenerator gère `create_all` correctement.
