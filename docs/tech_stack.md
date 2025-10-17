# Pile technologique de référence AEX

Cette proposition identifie les technologies de base pour implémenter l'architecture décrite dans `architecture.md`. Les choix favorisent l'interopérabilité, la scalabilité et la maintenabilité.

## Principes de sélection
- Privilégier des technologies open-source matures et largement supportées.
- Garantir la portabilité entre environnements (on-premise, cloud public).
- Assurer une observabilité native (logs, métriques, traces) et une intégration CI/CD fluide.

## Synthèse des choix

| Domaine | Langages / Frameworks | Services / Outils | Rationnel |
| --- | --- | --- | --- |
| Noyau (API, orchestration) | Python (FastAPI) ou Go (Go Fiber) | Kubernetes, Helm | APIs performantes, support asynchrone, facile à tester et containeriser. |
| File de jobs | Python + Dramatiq / Celery ou Go + Temporal | Redis / RabbitMQ (queue), Temporal server | Gestion robuste de jobs, reprise automatique, scheduling. |
| Gestion événements | Go + NATS ou Kafka Streams | NATS JetStream / Apache Kafka | Latence faible, persistance et relecture d'événements. |
| Stockage métadonnées | PostgreSQL 15 + SQLAlchemy | Patron `CQRS` léger (lecture/écriture) | Cohérence transactionnelle, richesse SQL. |
| Stockage vecteurs | Python + gRPC | Milvus / Weaviate | Optimisé pour la similarité vectorielle et la scalabilité horizontale. |
| Stockage fichiers | Services S3 compatibles | MinIO (dev) / AWS S3 (prod) | Standard de facto, versionnage natif. |
| Miniatures | Python + Pillow / OpenCV | CloudFront / Nginx cache | Transformation rapide, diffusion CDN. |
| Plug-ins IA | Python (PyTorch, ONNX Runtime), Rust (optimisation) | Serveurs Triton/ONNX, Docker | Flexibilité pour modélisation, accélération GPU possible. |
| UI | TypeScript + React + Vite | TailwindCSS, Zustand | Productivité front, composants réactifs. |
| Authentification | Keycloak / Auth0 | OpenID Connect, OAuth2 | Gestion centralisée des rôles et permissions. |
| Observabilité | OpenTelemetry, Prometheus, Grafana | Loki pour les logs, Tempo pour les traces | Stack intégrée, corrélation requête/événement. |
| CI/CD | GitHub Actions / GitLab CI | SonarQube, Trivy, Argo CD | Chaîne complète tests → sécurité → déploiement. |

## Détails par domaine

### Noyau & APIs
- **FastAPI** : typage statique via Pydantic, doc OpenAPI générée automatiquement, performance asynchrone.
- **Go Fiber** : alternative plus performante si besoin de latence minimale pour les services critiques.
- **Kubernetes** : standard pour orchestrer les services, permet autoscaling et stratégies de déploiement progressif.

### Orchestration & Jobs
- **Temporal** (Go/Python SDK) : workflows déclaratifs, gestion d'états longue durée, idéal pour pipelines ingestion/enrichissement.
- **Celery/Dramatiq** : options plus simples pour des tâches idempotentes, couplées à Redis ou RabbitMQ.

### Bus d'événements
- **NATS JetStream** : faible latence, sujets hiérarchiques adaptés aux événements `ImageIngested`/`EmbeddingComputed`.
- **Apache Kafka** : retenu si volumétrie massive, permet stream processing pour déduplication/analytics.

### Données
- **PostgreSQL** : stocke métadonnées, visages, tags, captions avec migrations via Alembic.
- **Milvus/Weaviate** : moteur vectoriel supportant HNSW/IVF, compatible gRPC/REST.
- **MinIO/S3** : stockage objet pour originaux et miniatures, versionnage et politiques de cycle de vie.

### Plug-ins IA
- **PyTorch** : fine-tuning, export ONNX pour production.
- **ONNX Runtime / TensorRT** : exécution optimisée CPU/GPU.
- **Triton Inference Server** : mutualise l'hébergement des modèles (embedder, classifier, captioner).

### Interface utilisateur
- **React + Vite** : démarrage rapide, hot reload, SSR optionnel.
- **TailwindCSS** : design system rapide.
- **Zustand** : gestion d'état légère et testable.
- **Storybook** : documentation des composants UI.

### Observabilité & Sécurité
- **OpenTelemetry** : instrumentation unifiée des services.
- **Prometheus/Grafana** : métriques, alerting.
- **Loki/Tempo** : logs et traces corrélées via `request_id`.
- **Keycloak** : gestion SSO, mapping des rôles `admin/éditeur/lecteur`.

### CI/CD
- **GitHub Actions** : pipeline standard (lint, tests, scans de sécurité, build images).
- **SonarQube** : analyse qualité code.
- **Trivy** : scan vulnérabilités des containers.
- **Argo CD** : déploiement GitOps vers Kubernetes.

## Recommandations complémentaires
- Définir des chartes Terraform pour provisionner l'infrastructure cloud.
- Automatiser les migrations de schémas via des jobs CI/CD dédiés.
- Publier des images Docker versionnées pour chaque plug-in.
- Documenter les SLIs/SLOs par service (latence ingestion, temps moyen `EmbeddingComputed`, etc.).
