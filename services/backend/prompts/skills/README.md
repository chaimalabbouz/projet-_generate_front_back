# Skills — Manuel du Fixer

Ce dossier est un **catalogue de bugs récurrents** rencontrés dans la génération de code backend. Chaque entrée décrit un symptôme observable, sa cause profonde, le fix correct, et surtout **les mauvaises pistes à ne PAS suivre**.

Le fixer DOIT utiliser ce dossier à chaque appel. Ce n'est ni facultatif, ni décoratif.

---

## Protocole obligatoire (à suivre dans l'ordre, sans exception)

### Étape 1 — Extraire le message d'erreur littéral
Avant toute action, identifier :
- Le type d'exception (`AttributeError`, `ResponseValidationError`, `TypeError`, `IntegrityError`, etc.)
- Le message exact (mot pour mot, pas paraphrasé)
- Le fichier et la ligne où l'exception est levée

Ne PAS reformuler ou résumer l'erreur avant cette étape.

### Étape 2 — Consulter l'index (OBLIGATOIRE, sans exception)
Lire `index.md` et comparer le message d'erreur avec chaque symptôme listé.

**Cette étape est obligatoire même si vous pensez connaître la réponse.** L'index existe précisément parce que l'intuition du LLM se trompe régulièrement sur les cas piégeux.

Pour chaque entrée de l'index, dire explicitement dans le raisonnement : « entrée X — matche / ne matche pas — raison ».

### Étape 3 — Décider le résultat du matching
Trois cas possibles :

- **Match clair** → annoncer l'entrée retenue et passer à l'étape 4.
- **Match partiel ou hésitation** → lire le fichier détail du candidat le plus probable ET annoncer l'hésitation dans le raisonnement.
- **Aucun match** → l'annoncer explicitement (« aucune entrée du skills.md ne correspond à ce symptôme »). C'est un résultat **valide et utile**, pas un échec. Passer alors à un raisonnement normal, mais sans oublier de suggérer qu'une nouvelle entrée pourrait être créée.

### Étape 4 — Lire le fichier détail
Lire INTÉGRALEMENT le fichier `entries/<nom>.md` correspondant à l'entrée retenue. Toutes les sections :
- Symptôme, Contexte, Cause profonde, Fix, **Anti-fixes**, Confirmation.

Ne PAS survoler. Les sections Cause et Anti-fixes contiennent la connaissance non triviale qui empêche les fausses pistes.

### Étape 5 — Appliquer le fix en verbalisant le raisonnement
Avant d'écrire le fichier corrigé, la réponse doit contenir une section explicite :

> **Diagnostic** : L'erreur `<message>` correspond à l'entrée `<nom>` du skills.
> **Cause** : `<résumé en une phrase de la cause profonde>`.
> **Fix appliqué** : `<action précise>` dans `<fichier>`.
> **Anti-fixes respectés** : `<lister ce que le skills interdit et que je ne fais donc PAS>`.

Cette verbalisation est obligatoire. Elle sert de trace pour le debug et empêche l'application mécanique du fix.

---

## Règles strictes non négociables

**R1.** L'index est consulté à CHAQUE appel, même si vous pensez avoir déjà vu le cas.

**R2.** Les sections **Anti-fixes** sont des INTERDICTIONS strictes. Même si une action interdite semble raisonnable, elle reste interdite. Le skills.md capture la connaissance des fausses pistes déjà tentées.

**R3.** Ne JAMAIS modifier un fichier de test (`tests/*.py`). Les tests sont la source de vérité. Corriger l'application, pas le test.

**R4.** Ne JAMAIS modifier le schéma ou le modèle « pour faire passer le test » si ce n'est pas justifié par une entrée du skills ou par la spec. Le fix doit résoudre la cause, pas masquer le symptôme.

**R5.** Si aucune entrée du skills ne matche, l'annoncer clairement. NE PAS forcer un match approximatif juste pour avoir quelque chose à appliquer.

---

## Convention des fichiers

- `index.md` — table de matching. Toujours envoyée au fixer.
- `entries/*.md` — un fichier par bug, lu à la demande via l'outil `read_file`.
- `_template.md` — squelette à copier pour créer une nouvelle entrée.

Chaque fichier d'entrée respecte STRICTEMENT le même format (voir `_template.md`).
