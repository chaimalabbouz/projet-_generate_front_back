# missing_not_null_column

## Symptôme
```
sqlalchemy.exc.IntegrityError: NOT NULL constraint failed: <table>.<column>
```

Une colonne marquée `nullable=False` dans le modèle SQLAlchemy n'a pas été fournie lors de l'insertion.

## Contexte
Se produit en général quand :
- Le schéma `<Entity>Create` n'inclut pas le champ, alors que le modèle l'exige.
- Le service ne transmet pas certains champs au constructeur du modèle.
- Le service tente de créer une entité avec `Model(**data.model_dump())` mais `data` ne contient pas le champ.

## Cause profonde
Divergence entre le contrat d'entrée (schéma `<Entity>Create`) et le contrat de stockage (modèle SQLAlchemy avec `nullable=False`). Un champ est requis en BDD mais optionnel — ou absent — dans le schéma.

## Fix correct
Deux stratégies selon la spec :

**Si le champ DOIT être fourni par l'utilisateur (c'est-à-dire obligatoire dans l'API) :**
Ajouter le champ au schéma `<Entity>Create` avec le bon type et sans valeur par défaut :
```python
class BlogCreate(BaseModel):
    title: str
    content: str
    <missing_field>: <type>    # ← ajouter ici
```

**Si le champ doit être rempli automatiquement côté serveur (ex : `created_at`, un UUID) :**
Ajouter un `default` côté modèle SQLAlchemy :
```python
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```
ou générer la valeur dans le service avant l'insertion.

Vérifier la spec dans le contexte fourni pour savoir laquelle des deux stratégies s'applique.

## Anti-fixes (INTERDIT)
- **NE PAS mettre la colonne à `nullable=True`** si la spec dit qu'elle est requise — on masque le problème, pas de résolution.
- **NE PAS ajouter une valeur bidon en dur dans le service** (`data["field"] = "unknown"`) — on stocke des données fausses.
- **NE PAS supprimer le test** ou changer le payload du test pour éviter le champ.

## Comment confirmer que c'est bien ce cas
Le message d'erreur donne la colonne exacte : `NOT NULL constraint failed: blogs.content`. Vérifier :
1. La colonne est-elle bien `nullable=False` dans le modèle ?
2. Le champ est-il présent dans le schéma `<Entity>Create` ?

Si oui à 1 et non à 2 → c'est bien ce bug.

## Métadonnées
- Ajouté le : entrée initiale
- Note : bug de désynchronisation entre schéma et modèle — cause fréquente d'échec sur les tests de création.
