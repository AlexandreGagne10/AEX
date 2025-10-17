# Guide GEMINI

Ce document rassemble les informations essentielles pour amorcer la conception et le développement du projet AEX.

## Vision
- Définir une plateforme modulaire et extensible pour les expériences d'agents.
- Favoriser l'interopérabilité entre les composants (modules d'IA, connecteurs, interfaces).
- Documenter systématiquement les décisions et hypothèses.

## Objectifs initiaux
1. Cartographier les domaines fonctionnels (planification, perception, action, mémoire).
2. Identifier les dépendances critiques entre modules.
3. Établir une stratégie d'intégration continue et de tests automatisés.

## Hypothèses de travail
- Les agents communiquent via des APIs gRPC/REST.
- Les modules doivent rester découplés et testables isolément.
- La configuration doit être déclarative (fichiers YAML/JSON).

## Ressources utiles
- `docs/architecture.md` pour la vue d'ensemble de l'architecture.
- `AGENT.MD` pour les conventions de contribution.
- `TODOLIST.MD` pour le suivi des tâches courantes.

## Questions ouvertes
- Quelle est la cadence de livraison souhaitée ?
- Quels environnements cibles doivent être pris en charge en priorité ?
- Quelles métriques mesurer pour évaluer les agents ?

Ajoutez vos réponses et découvertes au fil de l'avancement.
