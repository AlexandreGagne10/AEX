# Spécifications d'interfaces AEX

Ce document précise les contrats d'échange entre modules du socle AEX. Les interfaces sont décrites de manière agnostique vis-à-vis de la technologie d'implémentation (REST/gRPC), avec des indications sur les préconditions, postconditions et schémas d'échange.

## Principes généraux
- Toutes les interfaces synchrones doivent être idempotentes lorsque cela est pertinent (Hasher, Embedder, Indexer).
- Les requêtes et réponses utilisent des schémas JSON/Protobuf versionnés (`v1`, `v2`, …).
- Les erreurs applicatives sont normalisées via un code (`error.code`), un message et un champ `retryable`.
- Les événements sont publiés après validation par schéma (JSON Schema ou Protobuf) et contiennent un `event_id` unique.

## Interfaces du noyau

### API d'ingestion des fichiers
- **Endpoint** : `POST /ingest`
- **Entrée** :
  ```json
  {
    "path": "s3://bucket/key.jpg",
    "source": "batch-import",
    "ingest_options": {"generate_thumbnail": true}
  }
  ```
- **Préconditions** : le chemin est accessible et non déjà indexé (contrôle via hash si fourni).
- **Postconditions** : fichier enregistré, métadonnée créée avec statut `PENDING_HASH`, job `hash` planifié.
- **Erreurs** : `FILE_NOT_FOUND`, `INGEST_DUPLICATE`.

### Service de configuration
- **Endpoint** : `GET /config/{namespace}` & `PUT /config/{namespace}`.
- **Contrat** : charge/écrit un document YAML/JSON signé.
- **Contraintes** : versionnement (`version`, `updated_at`, `updated_by`), validation via schéma.

### Gestion de la file de jobs
- **Endpoint** : `POST /jobs`
- **Entrée** :
  ```json
  {
    "type": "embedding",
    "payload": {"image_id": "uuid", "embedding_kind": "clip"},
    "priority": "HIGH",
    "schedule_at": null
  }
  ```
- **Postconditions** : job persistant, ack envoyé au producteur. Worker abonné via `PULL /jobs/next?type=embedding`.
- **Erreurs** : `INVALID_PAYLOAD`, `QUEUE_UNAVAILABLE`.

## Interfaces de plug-ins

### Hasher
- **Signature** : `Hasher.compute(path: str) -> {sha256: str, perceptual_hash: str}`
- **Préconditions** : chemin lisible, image non corrompue.
- **Postconditions** : publication `ImageIngested` contenant les empreintes.
- **Erreurs** : `IO_ERROR`, `UNSUPPORTED_FORMAT`.

### Embedder
- **Signatures** :
  - `Embedder.image(image: bytes, kind: "clip"|"face") -> {vector: float[], dim: int, model_ref: str}`
  - `Embedder.text(text: str, lang: str) -> {vector: float[], dim: int, model_ref: str}`
- **Préconditions** : modèle actif pour le `kind`, dimensions cohérentes.
- **Postconditions** : publication `EmbeddingComputed` avec références `vector_id` et `image_id`.
- **Erreurs** : `MODEL_NOT_LOADED`, `UNSUPPORTED_LANGUAGE`.

### Detector
- **Signature** : `Detector.faces(image: bytes) -> [{bbox, landmarks, score}]`
- **Préconditions** : image ≤ taille maximale, formats gérés.
- **Postconditions** : création d'entrées `Visages`, génération de jobs `face-embedding`.
- **Erreurs** : `NO_FACE_FOUND` (non bloquant), `MODEL_RUNTIME_ERROR`.

### Classifier
- **Signature** : `Classifier.attributes(image: bytes | crop: bytes) -> {attributes: {hair_color, eye_color, nudity_score, ...}}`
- **Préconditions** : crop optionnel, image accessible.
- **Postconditions** : mise à jour des `Tags` avec `confidence` et provenance.
- **Erreurs** : `ATTRIBUTE_UNSUPPORTED`.

### Indexer
- **Signatures** :
  - `Indexer.add(id: str, vector: float[], space: "clip"|"face") -> {status: "indexed"}`
  - `Indexer.search(vector: float[], k: int, filters: {person_id?, nsfw_max?}) -> [{id, score}]`
- **Préconditions** : dimension du vecteur cohérente avec `space`, index disponible.
- **Postconditions** : vecteur persistant, résultat trié par score décroissant.
- **Erreurs** : `INDEX_UNAVAILABLE`, `DIMENSION_MISMATCH`.

### Captioner
- **Signature** : `Captioner.describe(image: bytes, lang: str) -> {text: str, confidence: float, model_ref: str}`
- **Préconditions** : langue supportée, modèle initialisé.
- **Postconditions** : enregistrement de `Captions`, publication `CaptionAdded`.
- **Erreurs** : `LANG_NOT_SUPPORTED`, `MODEL_TIMEOUT`.

### NSFWGate
- **Signature** : `NSFWGate.evaluate(image: bytes, context: {user_role, sensitivity}) -> {label: str, score: float}`
- **Préconditions** : règles de gouvernance chargées.
- **Postconditions** : mise à jour du statut NSFW, éventuellement masquage dans l'UI.
- **Erreurs** : `POLICY_NOT_FOUND`.

## Interfaces événementielles

### `ImageIngested`
- **Payload** :
  ```json
  {
    "event_id": "uuid",
    "image_id": "uuid",
    "sha256": "...",
    "perceptual_hash": "...",
    "ingested_at": "2025-10-17T12:00:00Z",
    "source": "batch-import"
  }
  ```
- **Consommateurs** : Embedder, Detector, Miniature, Audit.

### `EmbeddingComputed`
- **Payload** : contient `vector_id`, `image_id`, `kind`, `dim`, `model_ref`, `metrics`.
- **Consommateurs** : Indexer, Training/Finetuning.

### `FaceTagged`
- **Payload** : `face_id`, `image_id`, `cluster_id`, `tagger`.
- **Consommateurs** : Annotateur, Gouvernance, Indexer (visage).

### `CaptionAdded`
- **Payload** : `caption_id`, `image_id`, `lang`, `text`, `confidence`, `model_ref`.
- **Consommateurs** : ImageFinder, Training, Audit.

## Interfaces UI
- **Annotateur** : WebSocket `events` pour mise à jour en temps réel, REST `PUT /faces/{id}` pour assigner une personne.
- **ImageFinder** : `GET /search?mode=image|text|duplicate`, accepte des filtres structurés (`tags[key]=value`).
- **Training/Finetuning** : `POST /datasets` (sélection par tags, visages, captions), `POST /trainings` pour lancer un job.

## Sécurité & gouvernance
- Authentification via OIDC (`Authorization: Bearer`), scopes par domaine (`media:read`, `media:write`, `admin:audit`).
- Journalisation obligatoire : chaque appel reçoit un `request_id` propagé dans les logs.
- Les actions destructives exigent un rôle `admin` et sont doublées d'un événement d'audit.
