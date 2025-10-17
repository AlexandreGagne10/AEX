# Guide de contribution pour les agents

Ce document décrit la manière de travailler sur le dépôt AEX en respectant des pratiques homogènes.

## Flux de travail recommandé
1. **Analyse** : lire `GEMINI.MD` et `docs/architecture.md` pour comprendre le contexte.
2. **Planification** : enregistrer les tâches dans `TODOLIST.MD` avant de modifier le code.
3. **Implémentation** : travailler sur des branches dédiées avec des commits cohérents.
4. **Revue** : documenter les décisions dans les messages de commit et dans la section _Notes_ de `TODOLIST.MD`.

## Conventions de code
- Respecter les standards du langage utilisé (PEP 8 pour Python, rustfmt pour Rust, etc.).
- Ajouter des tests unitaires pour chaque fonctionnalité nouvelle ou corrigée.
- Préférer des fonctions pures et modulaires pour faciliter le test.

## Documentation
- Mettre à jour les fichiers Markdown pertinents lorsque de nouvelles fonctionnalités sont introduites.
- Ajouter un schéma ou un diagramme dans `docs/` pour toute modification architecturale majeure.

## Gestion des décisions
- En cas de choix important, documenter le raisonnement dans une section **Décision** de `TODOLIST.MD`.
- Indiquer la date, les auteurs et les conséquences attendues.

## Communication
- Utiliser des messages de commit en français clair, au présent, décrivant ce qui est fait.
- Mentionner les tickets ou tâches associés lorsqu'ils existent.

Ce guide peut évoluer : proposez des améliorations via des revues ou des issues dédiées.
