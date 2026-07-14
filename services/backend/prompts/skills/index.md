# Index des bugs connus

Table de matching. Toujours consultée en premier par le fixer.

Colonnes : **Entrée** (fichier dans `entries/`), **Symptôme** (message d'erreur littéral ou fragment distinctif), **Contexte** (indice pour lever l'ambiguïté).

Trié par fréquence d'occurrence (les plus courants en haut).

| Entrée | Symptôme (message d'erreur littéral) | Contexte de déclenchement |
|---|---|---|
| `none_required_shadowing` | `ResponseValidationError: {'type': 'none_required', ... 'msg': 'Input should be None'}` sur un champ qui devrait avoir une valeur | Champ Pydantic dont le nom est identique à un type Python natif (`date`, `type`, `id`, `list`...) |
| `service_arg_order_mismatch` | `AttributeError: 'Session' object has no attribute 'model_dump'` OU `AttributeError: 'int' object has no attribute 'query'` OU `'Session' object has no attribute '<field>'` | L'exception explose dans le service, mais la fonction service prise seule paraît correcte |
| `sqlite_date_type_mismatch` | `TypeError: SQLite Date type only accepts Python date objects as input` | Souvent la conséquence d'une "correction" précédente qui a changé un type Pydantic en `str` alors que la colonne SQL est `Date` |
| `wrong_pydantic_str_type_for_date` | `ResponseValidationError: {'type': 'string_type', ... 'msg': 'Input should be a valid string', 'input': datetime.date(...)}` | Le champ dans le schéma Pydantic est typé `str` alors que le modèle stocke un `date` |
| `missing_import` | `NameError: name 'Optional' is not defined` OU `name 'List' is not defined` OU `name 'date' is not defined` OU `name 'datetime' is not defined` | Un type est utilisé dans une annotation mais son import est absent en tête de fichier |
| `pydantic_orm_mode_missing` | `ResponseValidationError` sur un endpoint qui renvoie un objet SQLAlchemy, ou champs vides / manquants dans la réponse alors que la BDD est correcte | Le schéma Pydantic de réponse n'a pas `model_config = ConfigDict(from_attributes=True)` (Pydantic v2) ou `class Config: orm_mode = True` (v1) |
| `status_code_mismatch` | `assert 200 == 204` OU `assert 200 == 201` (comparant deux codes de SUCCÈS différents) | Le status_code du décorateur ne correspond pas à celui attendu. ⚠️ **NE PAS choisir ce skill si le code observé est 422** — un 422 signifie que Pydantic a rejeté le payload, la vraie cause est ailleurs : consulter d'abord `none_required_shadowing`, `wrong_pydantic_str_type_for_date`, `missing_import`, ou `missing_not_null_column`. |
| `missing_not_null_column` | `IntegrityError: NOT NULL constraint failed: <table>.<column>` | La route/service ne fournit pas une colonne pourtant marquée `nullable=False` dans le modèle |
| `foreign_key_not_seeded` | `IntegrityError: FOREIGN KEY constraint failed` OU l'objet parent référencé n'existe pas | Le test tente de créer une entité enfant sans que le parent ait été créé d'abord |
| `response_model_wrong_shape` | `ResponseValidationError` avec `loc: ('response', 0, ...)` sur un endpoint list, ou `loc: ('response', ...)` sur un endpoint single | `response_model` est mal typé : `List[X]` attendu mais `X` déclaré (ou l'inverse) |
| `route_prefix_mismatch` | `404 Not Found` sur un endpoint pourtant déclaré, ou test qui tape `/blog` alors que la route est `/blogs` (ou inverse) | Divergence entre le chemin utilisé dans le test et le path déclaré dans la route |
| `sqlalchemy_column_type_wrong` | `sqlalchemy.exc.CompileError` OU `ArgumentError: Column type not recognized` | Import ou type SQLAlchemy incorrect (ex : `String` utilisé pour une date, ou type inexistant) |
| `pydantic_v1_v2_mixup` | `AttributeError: 'FieldInfo' object has no attribute ...` OU `PydanticUserError: A non-annotated attribute was detected` OU utilisation de `.dict()` qui échoue | Mélange de syntaxe Pydantic v1 (`class Config`, `.dict()`) et v2 (`ConfigDict`, `.model_dump()`) dans le même code |
| `depends_get_db_missing` | `AttributeError: 'function' object has no attribute 'query'` OU `TypeError: 'Depends' object is not callable` sur une session | La route utilise `db: Session = get_db` au lieu de `db: Session = Depends(get_db)` |
| `circular_import` | `ImportError: cannot import name '<X>' from partially initialized module` | Deux fichiers s'importent mutuellement, souvent modèle ↔ schéma via des type hints |
| `alembic_migration_missing` | Test qui tape la BDD et reçoit `no such table: <table>` | La base de test n'a pas exécuté `Base.metadata.create_all()` avant les tests |
