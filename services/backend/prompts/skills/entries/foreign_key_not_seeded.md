# foreign_key_not_seeded

## Symptôme
```
sqlalchemy.exc.IntegrityError: FOREIGN KEY constraint failed
```

Une insertion utilise un id de parent qui n'existe pas dans la table parente.

## Contexte
Le test tente de créer une entité qui a une foreign key (ex : `Review` avec `recipe_id`), mais l'entité parente (`Recipe`) n'a pas été insérée d'abord. La FK pointe donc vers un id inexistant.

## Cause profonde
Chaîne de dépendance non respectée lors du seeding. Le générateur de test (`TestGenerator`) doit créer les parents AVANT les enfants, récursivement — sinon la contrainte FK échoue à l'insertion.

Note : dans le pipeline actuel, `TestGenerator._gen_seed_helper` gère cette cascade. Si l'erreur apparaît, c'est que soit le seed helper est incorrect, soit un fix précédent a modifié la structure du modèle et cassé la chaîne.

## Fix correct
**Ne PAS toucher au test** (il est généré par un composant déterministe et sa logique est correcte).

Chercher ce qui a été modifié dans le MODÈLE de l'entité :
- La FK a-t-elle disparu ou été renommée ?
- Le nom de la table parente a-t-il changé ?
- Le champ FK a-t-il été renommé (`recipe_id` → `parent_recipe_id`) sans mise à jour de la chaîne ?

Restaurer la définition de FK dans le modèle pour qu'elle corresponde à la spec :
```python
recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
```

Si l'entité parente elle-même n'est pas générée, vérifier que la task_queue inclut bien sa génération avant celle de l'enfant.

## Anti-fixes (INTERDIT)
- **NE PAS mettre la FK à `nullable=True` et créer l'entité orpheline** — corrompt les données.
- **NE PAS supprimer la contrainte FK dans le modèle** — perd l'intégrité référentielle.
- **NE PAS modifier le test pour ne pas créer le parent** — le test est correct.

## Comment confirmer que c'est bien ce cas
- L'erreur est-elle `FOREIGN KEY constraint failed` ?
- L'entité concernée a-t-elle bien une colonne FK dans son modèle ?

Si oui aux deux, chercher où la chaîne de seed s'est cassée.

## Métadonnées
- Ajouté le : entrée initiale
- Note : rare dans le pipeline actuel car le TestGenerator est déterministe et gère la cascade — mais peut apparaître si un fix précédent modifie le modèle.
