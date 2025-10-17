# Liste des tâches AEX

Utilisez cette liste pour suivre l'avancement des travaux. Cochez les éléments terminés et ajoutez des notes lorsque nécessaire.

## À faire
- *(à compléter)*

## En cours
- *(à compléter)*

## Terminées
- [x] Cartographier les modules existants décrits dans `docs/architecture.md`.
- [x] Définir les spécifications des interfaces entre modules.
- [x] Établir la pile technologique de référence (langages, frameworks, outils CI/CD).
- [x] Initialiser un squelette de service FastAPI couvrant ingestion, configuration et gestion des jobs.
- [x] Définir les modèles Pydantic et la validation pour les contrats REST décrits dans `docs/interface_specs.md`.
- [x] Couvrir le service par des tests unitaires de base (FastAPI TestClient) et un script de lancement.
- [x] Implémenter l'endpoint de récupération du prochain job pour les workers et gérer l'ordre de priorité.

## Notes
- 2025-10-17 : Planification de la session afin de documenter modules, interfaces et pile technologique.
- 2025-10-17 : Création de la cartographie des modules (`docs/module_map.md`), détaillage des interfaces (`docs/interface_specs.md`) et formalisation de la pile technologique (`docs/tech_stack.md`).
- 2025-10-18 : Préparation du développement initial du service FastAPI (contrats ingestion/configuration/jobs et tests).
- 2025-10-18 : Implémentation du service FastAPI, configuration de l'exception handler et couverture de tests automatisés (`pytest`).
- 2025-10-19 : Ajout d'un endpoint de leasing des jobs avec prise en compte de la priorité et des horaires de planification.

Mettez à jour ce fichier à chaque session de travail pour conserver une vue d'ensemble fiable.
