# Architecture modulaire pour la plateforme AEX

## Vue d'ensemble
Cette documentation décrit une architecture modulaire basée sur un noyau extensible et des plug-ins interchangeables pour la plateforme AEX. Elle couvre la vision fonctionnelle, les contrats entre composants, les modèles de données, ainsi que les pipelines opérationnels et la feuille de route prévisionnelle.

## Noyau et services partagés
- **Gestion des fichiers** : prise en charge du stockage et des métadonnées basiques.
- **File d'attente de jobs** : ordonnancement des traitements batch et temps réel.
- **Gestion des événements** : diffusion et consommation des événements fonctionnels.
- **Collecte des logs** : traçabilité et observabilité des opérations.
- **Gestion de la configuration** : paramètres système et des plug-ins.

## Magasin de données
- **Métadonnées** : informations descriptives sur les images et leurs traitements.
- **Vecteurs** : représentations générées par les modèles d'embedding.
- **Miniatures** : prévisualisations optimisées pour l'UI.
- **Index de similarité** : structures dédiées aux recherches vectorielles et perceptuelles.

## Bus d'événements
Les événements clés orchestrant les flux sont :
- `ImageIngested`
- `EmbeddingComputed`
- `FaceTagged`
- `CaptionAdded`

## Plug-ins et outils UI
### Plug-ins interchangeables
- **Hasher**
- **Embedder**
- **Detector**
- **Classifier**
- **Indexer**
- **Captioner**
- **NSFWGate**

### Outils UI connectés via un contrat commun
- **Annotateur**
- **Training / Finetuning**
- **ImageFinder**

## Contrats fonctionnels
- `Hasher.compute(path) -> {sha256, perceptual_hash}`
- `Embedder.image(img) -> vector`
- `Embedder.text(text) -> vector`
- `Detector.faces(img) -> [bbox, landmarks]`
- `Classifier.attributes(img|crop) -> {hair:…, eyes:…, nudity:…, conf…}`
- `Captioner.describe(img, lang) -> {text, conf}`
- `Indexer.add(id, vector, space)`
- `Indexer.search(vector, k) -> [(id, score)]`

## Modèle de données conceptuel
### Images
- `id`
- `chemin`
- `taille`
- `empreintes` (sha256, pHash)
- `exif`
- `statut`

### Vecteurs
- `image_id`
- `type` (clip | face | attr | caption)
- `dim`
- `index_ref`

### Visages
- `id`
- `image_id`
- `bbox`
- `vector_ref`
- `cluster_id`
- `person_id?`

### Personnes
- `id`
- `nom` (unique)
- `alias?`
- `notes`

### Tags
- `image_id`
- `clé`
- `valeur`
- `confiance`

### Captions
- `image_id`
- `texte`
- `langue`
- `confiance`
- `provenance`

### Liens
- `duplicate_of`
- `groups`

## Pipelines opérationnels
### Ingestion
1. Scan des fichiers.
2. Calcul des empreintes.
3. Extraction EXIF.
4. Génération des miniatures.
5. Publication `ImageIngested`.

### Enrichissement (événementiel ou batch)
- Calcul des embeddings (généraux et visage).
- Extraction d'attributs.
- Évaluation NSFW.
- Génération de captions.

### Indexation
- Ajout et mise à jour des vecteurs dans les index dédiés (généraux et visages).

### Consolidation
- Groupement des doublons.
- Fusion des tags.
- Historisation des décisions (audit).

## Algorithmes et règles clés
### Détection de doublons
- **Exacts** : comparaison `sha256`.
- **Proches** : seuil sur la distance de `perceptual_hash`.
- **Très proches** : similarité vectorielle + vérification taille/ratio.
- **Sortie** : groupes avec un représentant et options `Fusionner` / `Ignore`.

### Recherche par image de référence
1. Embedding de l'image requête.
2. Top-k similaires.
3. Re-rank avec pHash/EXIF.
4. Filtres optionnels : personne, nudité, date, dimensions.

### Recherche par critères
- **Sémantique** : embedding texte → recherche vectorielle.
- **Structuré** : filtres `tags(key, value, conf ≥ seuil)`.
- **Combinaison** : pondération entre score texte et filtres.

### Association de noms aux visages
- Détection → vecteurs visage → clustering non supervisé.
- UI pour nommer un cluster et propager l'étiquette.
- Rétroaction : correction, mise à jour des centroïdes et historique.

### Captioning de masse
- Planificateur de jobs (lot, reprise).
- Captions multilingues optionnels.
- Déduplication par empreinte (image + modèle + langue).
- Post-filtrage pour retirer informations sensibles si NSFW activé.

## Outils et comportements
### Annotateur d'image
- Affichage des boîtes, clusters, tags.
- Actions : renommer personne, corriger attributs, masquer NSFW, valider doublons.

### Training / Finetuning
- Sélection de datasets par tags/visages/captions.
- Gestion des splits, suivi de métriques, versionnage.
- Export / import de modèles.

### ImageFinder
- Trois onglets : Doublons, Par image, Par critères.
- Tri, comparaison côte-à-côte, actions de lot.

## Gouvernance et sécurité
- Rôles (admin / éditeur / lecteur).
- Piste d'audit (qui renomme / supprime).
- Masquage des vignettes sensibles (NSFW) avec seuils configurables.
- Politiques de suppression / archivage.
- Exports portables (parquet + media).

## Qualité et évaluation
- Jeux de validation internes :
  - Doublons : séries artificielles (recadrage, rotation, compression).
  - Attributs : échantillons annotés manuellement.
  - Recherche : R@k, mAP, nDCG.
- Télémétrie : temps/1000 images, mémoire, taux d'erreur, % auto-assign correct.

## Roadmap (capacités)
- **Semaine 1** : noyau, schéma, ingestion, déduplication exact/pHash.
- **Semaine 2** : embeddings généraux, recherche par image & texte.
- **Semaine 3** : visages (détection, clustering, annotation).
- **Semaine 4** : attributs, filtres structurés, NSFW.
- **Semaine 5** : captioning de masse, export datasets.
- **Semaine 6** : outil Training, versionnage, améliorations UX.
