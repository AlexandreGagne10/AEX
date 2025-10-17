# Cartographie des modules AEX

Cette cartographie synthétise les composants décrits dans `architecture.md` afin de clarifier leurs responsabilités, leurs dépendances et les points d'intégration clés.

## Vue synthétique

| Domaine | Module | Responsabilités principales | Interfaces clés | Dépendances amont / aval |
| --- | --- | --- | --- | --- |
| Noyau | Gestion des fichiers | Indexation des médias, stockage des métadonnées, vérification d'intégrité. | API d'ingestion, événements `ImageIngested`. | Système de fichiers / objet, file de jobs, collecte de logs. |
| Noyau | File d'attente de jobs | Orchestration des traitements batch et temps réel, priorisation, reprise. | API Planificateur, workers plug-ins. | Gestion configuration, collecte de logs. |
| Noyau | Gestion des événements | Publication/consommation d'événements métiers, routage. | Bus événementiel, schémas d'événements. | Collecte des logs, plug-ins, UI. |
| Noyau | Collecte des logs | Agrégation, enrichissement et exposition des journaux techniques/fonctionnels. | API observabilité, tableaux de bord. | Tous les modules. |
| Noyau | Gestion de la configuration | Centralisation des paramètres système et plug-ins, versionnage. | API de configuration, fichiers déclaratifs. | Tous les modules. |
| Données | Métadonnées | Persistances des descripteurs de médias et états de traitement. | DAO/Repository, API GraphQL/REST. | Gestion des fichiers, plug-ins. |
| Données | Vecteurs | Stockage des embeddings image/texte/visage. | API vecteurs, index. | Embedder, Indexer. |
| Données | Miniatures | Génération et mise à disposition des aperçus. | Service de thumbnail, CDN interne. | Gestion des fichiers, UI. |
| Données | Index de similarité | Recherche vectorielle, métriques de proximité. | API `Indexer.add/search`. | Vecteurs, Embedder, UI. |
| Événements | Bus d'événements | Canal unique pour `ImageIngested`, `EmbeddingComputed`, `FaceTagged`, `CaptionAdded`. | Contrats d'événements versionnés. | Gestion des événements, plug-ins, UI. |
| Plug-ins | Hasher | Calcul SHA-256 et pHash. | `Hasher.compute`. | Gestion des fichiers, Métadonnées. |
| Plug-ins | Embedder | Embeddings CLIP/visage/texte. | `Embedder.image/text`. | File de jobs, Vecteurs, Index. |
| Plug-ins | Detector | Détection de visages et landmarks. | `Detector.faces`. | File de jobs, Vecteurs, Visages. |
| Plug-ins | Classifier | Extraction d'attributs (hair, eyes, nudity). | `Classifier.attributes`. | File de jobs, Tags, UI. |
| Plug-ins | Indexer | Gestion des index de similarité. | `Indexer.add/search`. | Vecteurs, Bus d'événements. |
| Plug-ins | Captioner | Génération de descriptions multilingues. | `Captioner.describe`. | File de jobs, Captions. |
| Plug-ins | NSFWGate | Filtrage des contenus sensibles. | API `nsfw.evaluate`. | File de jobs, UI, Gouvernance. |
| UI | Annotateur | Annotation et validation humaine. | API UI unifiée, Websocket événementiel. | Bus d'événements, Tags, Visages. |
| UI | Training / Finetuning | Gestion des datasets, suivi des modèles. | API Training, stockage modèles. | Vecteurs, Tags, Gouvernance. |
| UI | ImageFinder | Recherche doublons/similarité. | API recherche, index. | Indexer, Miniatures, Captions. |
| Gouvernance | Rôles & audit | Contrôle d'accès, historique, masquage NSFW. | API IAM, journaux d'audit. | Tous les modules exposés aux utilisateurs. |

## Détails par domaine

### Noyau et services partagés
- **Gestion des fichiers** : prend en charge l'ingestion, le stockage physique (FS ou objet) et maintient la cohérence avec les métadonnées.
- **File d'attente de jobs** : planifie les traitements asynchrones (hash, embeddings, détection) avec gestion de priorités et reprise.
- **Gestion des événements** : centralise la publication, la validation des schémas et le routage vers les consommateurs.
- **Collecte des logs** : consolide les journaux techniques et fonctionnels, fournit des métriques et alertes.
- **Gestion de la configuration** : maintient la configuration déclarative (YAML/JSON) pour les plug-ins et services.

### Magasin de données
- **Métadonnées** : structure principale décrivant l'état des images, tags, statuts de pipelines.
- **Vecteurs** : tables/collections pour embeddings (CLIP, visage, attributs, captions) avec références aux index.
- **Miniatures** : service spécialisé générant des vignettes optimisées pour l'UI.
- **Index de similarité** : moteurs spécialisés (FAISS, Milvus…) branchés sur les vecteurs.

### Bus d'événements
- Garantit l'acheminement des événements clés (`ImageIngested`, `EmbeddingComputed`, `FaceTagged`, `CaptionAdded`) et leur idempotence.

### Plug-ins et outils UI
- Plug-ins interchangeables exécutés via le planificateur (Hasher, Embedder, Detector, Classifier, Indexer, Captioner, NSFWGate).
- Outils UI consommant les APIs consolidées : Annotateur, Training/Finetuning, ImageFinder.

### Gouvernance et sécurité
- Rôles (admin, éditeur, lecteur) appliqués aux APIs UI et de gestion.
- Audit des actions utilisateurs (renommage, suppression, masquage NSFW).

## Relations et flux principaux
1. **Ingestion** : Gestion des fichiers → Hasher → Métadonnées → Bus d'événements (`ImageIngested`).
2. **Enrichissement** : File de jobs → (Embedder, Detector, Classifier, Captioner, NSFWGate) → Vecteurs/Tags/Captions → Bus d'événements (`EmbeddingComputed`, `FaceTagged`, `CaptionAdded`).
3. **Indexation** : Vecteurs → Indexer → Index de similarité → Recherche UI.
4. **Consolidation** : Processus métiers (doublons, fusion) orchestrés via la file de jobs et le bus d'événements.

## Points d'attention
- Les plug-ins doivent rester stateless et configurés via le service de configuration.
- Les événements doivent être versionnés et validés par schémas pour éviter les régressions.
- La gouvernance doit couvrir la traçabilité des actions critiques (suppression, renommage, masquage).
