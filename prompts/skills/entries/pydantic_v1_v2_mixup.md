# pydantic_v1_v2_mixup

## Symptôme
Une des formes suivantes :
```
AttributeError: 'FieldInfo' object has no attribute '<X>'
PydanticUserError: A non-annotated attribute was detected: '<field>'
AttributeError: '<Model>' object has no attribute 'dict'    # v2 utilise model_dump()
TypeError: BaseModel.model_config must be a ConfigDict, got <class 'type'>
```

## Contexte
Le code mélange la syntaxe Pydantic v1 et v2 dans le même fichier, ou selon la version installée. Le LLM du backend agent bascule parfois entre les deux styles.

Différences clés :
- **v1** : `class Config: orm_mode = True`, `.dict()`, `.parse_obj()`, `class Config: allow_population_by_field_name = True`.
- **v2** : `model_config = ConfigDict(from_attributes=True)`, `.model_dump()`, `.model_validate()`, `model_config = ConfigDict(populate_by_name=True)`.

## Cause profonde
Pydantic v2 (sorti mi-2023) est incompatible avec certains patterns v1. Utiliser du v1 dans un projet v2 (ou l'inverse) génère des erreurs souvent obscures.

## Fix correct
1. Vérifier la version installée (`pip show pydantic`).
2. Si v2 → aligner tout sur v2 :
   - Remplacer `class Config: orm_mode = True` par `model_config = ConfigDict(from_attributes=True)`.
   - Remplacer `.dict()` par `.model_dump()`.
   - Remplacer `.parse_obj()` par `.model_validate()`.
   - Importer `ConfigDict` depuis `pydantic`.
3. Si v1 → aligner sur v1 (rare aujourd'hui, mais possible pour du legacy).

## Anti-fixes (INTERDIT)
- **NE PAS mélanger les deux syntaxes** dans le même fichier — cause d'incompréhension et de nouveaux bugs.
- **NE PAS installer les deux versions** — Pydantic ne cohabite pas.

## Comment confirmer que c'est bien ce cas
Le fichier utilise à la fois `class Config` ET `model_config`, ou appelle `.dict()` dans un projet v2, ou vice versa.

## Métadonnées
- Ajouté le : entrée initiale
- Note : dans le pipeline actuel, le projet est Pydantic v2 — donc toujours aligner sur v2.
