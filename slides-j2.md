---
marp: true
theme: your-theme
paginate: true
title: "RAG pour données actuarielles — Jour 2"
header: "Conception d'un système RAG — Jour 2"
footer: "© Claude et Frédéric Gaurat 2026"
---

# Conception d'un système RAG
## pour l'exploitation de données actuarielles

### Jour 2 — Embeddings & Recherche sémantique

**Durée** : 7h  |  **Prérequis** : Jour 1 complété  |  **Public** : Développeurs / Data analysts

---

# Programme — Jour 2

## Matin
- Modèles d'embedding
- Stockage et indexation vectorielle

## Après-midi
- Recherche et retrieval
- Prompting et qualité des réponses RAG

---

<!-- _class: lead -->
# Jour 2 — Matin
## Modèles d'embedding et stockage vectoriel

---

<!-- _class: lead -->
# Modèles d'embedding

---

# Qu'est-ce qu'un embedding ?

- Représentation numérique d'un texte sous forme de vecteur
- Un vecteur de N dimensions (ex : 384, 768, 1536)
- Les textes **sémantiquement proches** ont des vecteurs **proches dans l'espace**
- Permet la comparaison mathématique entre textes

> "Le sinistre auto" et "l'accident de voiture" auront des vecteurs très proches

---

# De la phrase au vecteur — intuition géométrique

- Le modèle encode chaque phrase en un point dans un espace de haute dimension
- Des phrases au sens proche se retrouvent dans la même région de l'espace
- La distance entre deux points reflète la différence sémantique

```
         ^  dim 2
         |
  "incendie"  x
         |          x "feu"
         |    x "sinistre auto"
         |                  x "accident voiture"
         +----------------------------> dim 1
```

- En RAG : on cherche les voisins les plus proches du vecteur de la requête

---

# La similarité sémantique — définition

- Mesure à quel point deux textes veulent dire "la même chose"
- Indépendante des mots exacts utilisés (synonymes, reformulations)
- S'appuie sur la position relative des vecteurs dans l'espace
- Valeur entre 0 (sans rapport) et 1 (identiques sémantiquement)

> "Garantie responsabilité civile" et "RC tiers" partagent le même sens métier — leur similarité sera élevée même si aucun mot n'est commun

---

# Similarité cosinus — principe

- Mesure l'**angle** entre deux vecteurs, pas leur distance absolue
- Formule : `cos(θ) = (A · B) / (||A|| × ||B||)`
- Avantage : insensible à la longueur du texte (un résumé vs un document complet)
- Score = 1 → vecteurs parallèles (même sens), Score = 0 → orthogonaux (sens sans rapport)

```
         ^
    B /  |
      /θ |
     /   |
    /    +----------> A     cos(θ) proche de 1 : A et B très similaires
```

---

# Similarité cosinus — interprétation pratique

- **> 0.85** : textes quasi-identiques ou très fortement liés
- **0.70 – 0.85** : même sujet, formulations différentes (cas courant en RAG)
- **0.50 – 0.70** : domaine commun, thématique voisine
- **< 0.50** : peu de rapport sémantique

> Exemple actuariel : clause "non-garantie en cas d'alcool au volant" et clause "exclusion pour conduite en état d'ivresse" → similarité ≈ 0.88 ; même clause vs article sur la météo → similarité ≈ 0.12

---

# Panorama des modèles d'embedding

- **OpenAI Embeddings** : `text-embedding-3-small/large` — API cloud, 1536 dims
- **Sentence Transformers** : famille open-source, auto-hébergeable, très variée
- **Modèles multilingues** : couvrent le français sans fine-tuning (ex : multilingual-mpnet)
- **Modèles spécialisés** : fine-tunés sur des domaines (médical, juridique, financier)
- **CamemBERT / RoBERTa** : modèles français natifs, performants sur textes métier

---

# Sentence Transformers — présentation

- Bibliothèque open-source basée sur HuggingFace Transformers
- Optimisée pour encoder des **phrases entières** en un seul vecteur dense
- Entraînée avec une architecture siamoise sur des paires de phrases similaires
- Hébergeable en local — pas de dépendance à une API tierce
- Compatible avec FAISS, ChromaDB, Weaviate et tous les vector stores majeurs

---

# Sentence Transformers — modèles recommandés

- `all-MiniLM-L6-v2` : léger (22M params), rapide, bon pour l'anglais
- `paraphrase-multilingual-mpnet-base-v2` : multilingue 50 langues dont le français
- `all-mpnet-base-v2` : meilleure qualité anglais, plus lourd
- `distiluse-base-multilingual-cased-v2` : compromis vitesse/qualité multilingue
- Critère de choix : langue cible, contrainte de latence, volume à vectoriser

---

# Modèles multilingues — intérêt pour le français

- Les données actuarielles Groupama sont quasi exclusivement en **français**
- Un modèle anglophone dégrade la qualité des embeddings sur textes français
- Les modèles multilingues ont été entraînés sur des corpus incluant le français
- Alternative : fine-tuner un modèle sur des paires de phrases du domaine assurance
- Référence de benchmark : MTEB (Massive Text Embedding Benchmark) — inclut le français

> CamemBERT est une option si les textes sont 100 % français et très spécialisés

---

# all-MiniLM-L6-v2 — caractéristiques

- **Dimensions** : 384 — vecteurs compacts, stockage réduit
- **Langue principale** : anglais (performances dégradées en français)
- **Vitesse** : très rapide — idéal pour prototypage et gros volumes
- **Taille du modèle** : ~22 Mo — s'exécute facilement sans GPU
- **Limite** : longueur maximale de 256 tokens par chunk (attention aux gros paragraphes)

---

# paraphrase-multilingual-mpnet-base-v2 — caractéristiques

- **Dimensions** : 768 — vecteurs plus riches que MiniLM
- **Langue** : 50 langues dont le français, l'allemand, l'espagnol
- **Vitesse** : modérée — environ 3× plus lent que MiniLM
- **Taille du modèle** : ~970 Mo — nécessite un peu plus de RAM
- **Forces** : excellente qualité sur textes multilingues, robuste aux reformulations

---

# Comparatif des modèles d'embedding

| Modèle | Dimensions | Langue | Vitesse | Cas d'usage |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | 384 | Anglais | Très rapide | Prototype, POC |
| all-mpnet-base-v2 | 768 | Anglais | Moyenne | Production anglaise |
| paraphrase-multilingual-mpnet-base-v2 | 768 | 50 langues | Moyenne | Production française |
| distiluse-base-multilingual-cased-v2 | 512 | 15 langues | Rapide | Multilingue léger |
| text-embedding-3-small (OpenAI) | 1536 | Multilingue | API | SaaS, sans infra |
| CamemBERT | 768 | Français | Moyenne | Textes 100 % FR |

---

# Évaluation de la qualité des embeddings

- **Retrieval@K** : parmi les K chunks retournés, combien sont pertinents ?
- **MRR (Mean Reciprocal Rank)** : rang moyen du premier chunk correct
- **NDCG** : mesure la qualité du classement (les meilleurs résultats en tête)
- Comparer au moins deux modèles candidats sur le même jeu de questions
- Un bon score sur MTEB ne garantit pas un bon score sur votre domaine métier

---

# Évaluation sur des données métier — méthode

- Constituer un **jeu de 20 à 50 paires** question / chunk de référence (gold set)
- Questions réalistes : "Quelle est la franchise en cas de bris de glace ?"
- Vectoriser le corpus avec chaque modèle candidat, interroger avec les mêmes questions
- Mesurer le taux de hit (chunk de référence dans le top 5) pour chaque modèle
- Impliquer un expert métier pour valider la pertinence du gold set

> Sur des clauses de contrats IARD, un modèle multilingue surpasse souvent MiniLM de 10 à 20 points de Retrieval@5

---

# Biais des embeddings — pièges à connaître

- Les modèles sont entraînés sur du web généraliste — le jargon assurance peut être mal représenté
- "Provision" en assurance ≠ "provision" en comptabilité — le modèle peut confondre
- Les abréviations métier (IARD, RC, DTA) sont souvent mal encodées
- Un texte très court (3 mots) produit un vecteur moins stable qu'une phrase complète
- Solution partielle : inclure un contexte de section dans chaque chunk avant vectorisation

---

# Dimension des vecteurs et performance

- **Plus de dimensions** → représentation plus riche → meilleure qualité (en général)
- **Contrepartie** : stockage plus élevé, calculs de similarité plus lents
- 384 dims → 1.5 Ko par vecteur ; 768 dims → 3 Ko ; 1536 dims → 6 Ko
- Pour 1 million de chunks : 1.5 Go vs 6 Go en RAM/disque
- Les gains de qualité au-delà de 768 dims sont souvent marginaux sur des corpus métier

---

# Coût de la vectorisation — calcul et optimisation

- **Coût one-shot** : vectorisation initiale du corpus (accepter un temps long)
- **Coût incrémental** : re-vectoriser uniquement les nouveaux documents ou chunks modifiés
- Vectoriser en batch (256 chunks à la fois) pour maximiser le débit GPU/CPU
- Mettre en cache les vecteurs calculés — ne jamais re-vectoriser un chunk inchangé
- Estimation : MiniLM vectorise ~1 000 phrases/seconde sur CPU standard

> 100 000 chunks × 384 dims = ~150 Mo de vecteurs ; calcul initial ≈ 100 secondes sur CPU

---

# Bonnes pratiques de choix de modèle d'embedding

- Commencer par `paraphrase-multilingual-mpnet-base-v2` pour tout texte en français
- Évaluer sur un gold set métier avant de vectoriser tout le corpus
- Préférer un modèle auto-hébergé si la confidentialité des données est un enjeu
- Ne pas mélanger les modèles dans un même index vectoriel (incompatibilité des espaces)
- Documenter le modèle et la version utilisés — changer de modèle = tout re-vectoriser

---

# Ce qu'on retient — Modèles d'embedding

- Un embedding transforme un texte en vecteur numérique comparable mathématiquement
- La similarité cosinus mesure la proximité sémantique entre deux textes
- Choisir un modèle multilingue pour du français (paraphrase-multilingual ou camembert)
- Évaluer le modèle sur des exemples du domaine métier avant de vectoriser tout le corpus

---

---

<!-- _class: section -->

# Stockage et indexation vectorielle

---

# Pourquoi une base vectorielle ?

- Les SGBD relationnels classiques ne savent pas comparer efficacement des vecteurs de 768 dimensions
- La recherche "les 5 documents les plus proches" exige une métrique de distance, pas un `WHERE` exact
- Contexte Groupama : corpus de plusieurs millions de documents actuariels (contrats, sinistres, circulaires)
- Sans index spécialisé, une recherche exhaustive serait trop lente pour un usage temps réel
- La base vectorielle joue le rôle d'un moteur de recherche sémantique à l'intérieur du pipeline RAG

---

# Options de stockage — panorama

- **Bases dédiées** : ChromaDB, Qdrant, Weaviate, Pinecone — optimisées pour les vecteurs
- **Extensions SQL** : pgvector (PostgreSQL), sqlite-vss (SQLite), SQL Server (types vectoriels natifs)
- **Bibliothèques en mémoire** : FAISS (Meta) — idéal pour le calcul batch offline
- **Critères de choix** : volume, infrastructure existante, budget opérationnel, confidentialité
- En contexte entreprise, l'intégration avec le SI existant prime souvent sur la performance brute

---

# SQL Server — support des types vectoriels

- SQL Server 2022+ introduit le type `VECTOR(n)` natif et la fonction `VECTOR_DISTANCE()`
- Avantage stratégique : réutilise les licences, les équipes DBA et les outils BI existants
- Les politiques de sécurité (Active Directory, chiffrement TDE) s'appliquent directement
- Contrainte : les index vectoriels approximatifs (HNSW) sont disponibles à partir d'Azure SQL
- Recommandation Groupama : solution prioritaire si le corpus tient sous 10 M de documents

---

# SQL Server — recherche par similarité

- La recherche s'écrit en SQL standard avec `VECTOR_DISTANCE('cosine', v1, v2)`
- `ORDER BY distance ASC LIMIT k` retourne les k plus proches voisins
- Filtrage hybride possible : `WHERE produit = 'RC Auto' ORDER BY distance LIMIT 5`
- Intégration directe avec les pipelines ETL/SSIS et les tableaux de bord Power BI
- Audit et traçabilité natifs via les journaux SQL Server — conformité RGPD simplifiée

---

# SQLite + sqlite-vss — présentation et avantages dev local

- Extension SQLite qui expose des fonctions de recherche vectorielle sans serveur
- **Zéro infrastructure** : un seul fichier `.db`, aucun daemon, aucun port réseau à ouvrir
- Idéal pour les POC, les notebooks de prototypage et les environnements de développement isolés
- Limite pratique : au-delà de ~500 000 vecteurs les performances se dégradent sensiblement
- Transition vers la prod : le schéma et les requêtes SQL restent quasi-identiques sur pgvector

---

# ChromaDB — présentation

- Base vectorielle open source conçue spécifiquement pour les applications LLM et RAG
- API Python minimaliste : `collection.add()`, `collection.query()` — courbe d'apprentissage très faible
- Mode embarqué (in-process) ou mode serveur HTTP selon le besoin
- Stockage persistant sur disque ou en mémoire ; intégration native avec LangChain et LlamaIndex
- Limite : pas de haute disponibilité native, pas de gestion fine des droits — usage dev/prototypage

---

# FAISS (Meta) — présentation

- Facebook AI Similarity Search : bibliothèque C++ avec bindings Python, conçue pour la vitesse
- Supporte des milliards de vecteurs grâce à la compression par quantification (PQ, SQ)
- Plusieurs types d'index : `IndexFlatL2`, `IndexIVFFlat`, `IndexHNSWFlat`…
- **Pas de persistance native** : l'index doit être sérialisé (`faiss.write_index`) et rechargé à chaque démarrage
- Usage recommandé : calcul batch offline (re-indexation nocturne, scoring en masse de sinistres)

---

# pgvector (PostgreSQL) — présentation

- Extension PostgreSQL officielle (`CREATE EXTENSION vector`) — disponible sur RDS, Azure Database
- Ajoute le type `VECTOR(n)`, les opérateurs `<->` (L2), `<=>` (cosinus), `<#>` (produit scalaire)
- Index HNSW et IVFFlat disponibles ; intégration transparente avec l'ORM SQLAlchemy
- Transactions ACID : la mise à jour d'un vecteur et de ses métadonnées est atomique
- Recommandé si Groupama dispose déjà d'une infrastructure PostgreSQL et d'équipes DBA formées

---

# Comparatif des solutions de stockage vectoriel

| Solution | Usage | Avantages | Inconvénients |
|---|---|---|---|
| SQL Server | Production enterprise | Intégration existante | Configuration complexe |
| SQLite-vss | Dev local / POC | Zéro infrastructure | Limité en volume |
| ChromaDB | Dev / prototypage | API simple | Pas enterprise-grade |
| FAISS | Calcul batch | Très performant | Pas de persistance native |
| pgvector | PostgreSQL existant | SQL familier | Paramétrage fin requis |

---

# L'index vectoriel — rôle et fonctionnement

- Sans index : recherche exhaustive = comparer la requête aux N vecteurs un par un (O(N·d))
- Avec index : la structure précompute des raccourcis pour éliminer les candidats improbables
- L'index ne stocke pas les textes originaux — il pointe vers des identifiants de documents
- Compromis fondamental : précision (recall) vs vitesse — plus l'index est approximatif, plus il est rapide
- Paramétrer l'index = ajuster ce compromis selon le SLA métier (temps de réponse vs pertinence)

---

# Index plat vs index approximatif

- **Index plat (Flat / Exact)** : calcule toutes les distances, précision = 100%, lent sur grand corpus
- **Index approximatif (ANN)** : sacrifie quelques pourcents de recall pour gagner 10x à 100x en vitesse
- HNSW et IVF sont les deux familles d'index ANN les plus utilisées en production
- Règle pratique : index plat si < 100 000 vecteurs ; index ANN au-delà
- Contexte actuariel : un recall de 95 % est généralement suffisant pour la recherche de jurisprudence ou de clauses

---

# HNSW — principe et paramètres (ef_construction, M)

- **Hierarchical Navigable Small World** : graphe de proximité multi-couche, navigation par sauts
- Construction : chaque vecteur est connecté à ses `M` voisins les plus proches dans la couche courante
- `M` (défaut 16) : nombre de connexions par nœud — augmenter améliore le recall, augmente la RAM
- `ef_construction` (défaut 100) : taille de la liste de candidats pendant la construction — qualité vs temps de build
- `ef_search` (à l'inférence) : taille du faisceau de recherche — augmenter améliore le recall au coût du temps

---

# IVF — principe et paramètres (nlist, nprobe)

- **Inverted File Index** : le corpus est divisé en `nlist` clusters via k-means (comme une bibliothèque à rayons)
- À la requête, seuls les `nprobe` clusters les plus proches sont explorés — économie de calcul
- `nlist` (ex. 256 pour 1 M de vecteurs) : plus de clusters = recherche plus fine mais build plus long
- `nprobe` (ex. 16) : plus de clusters sondés = meilleur recall mais plus lent — tuner selon le SLA
- Nécessite une phase d'entraînement préalable sur un échantillon représentatif du corpus

---

# Choisir l'index selon le volume de données

| Volume | Index recommandé | Raison |
|---|---|---|
| < 100 k vecteurs | Index plat | Précision maximale, vitesse suffisante |
| 100 k – 1 M | HNSW | Bon recall, faible latence, RAM raisonnable |
| 1 M – 100 M | IVF + PQ | Compression indispensable, scalabilité |
| > 100 M | IVF + PQ + sharding | Distribution horizontale requise |

- Corpus Groupama estimé à ~5 M de documents → zone IVF ou HNSW avec compression quantization

---

# Organisation des métadonnées en base

- Les vecteurs seuls sont insuffisants : il faut retrouver le texte source, la date, l'auteur, le produit
- Stratégie 1 : stocker métadonnées et vecteur dans la même table (pgvector, SQL Server)
- Stratégie 2 : table vectorielle + table métadonnées liées par un `chunk_id` (join au moment de la restitution)
- Champs clés pour un corpus actuariel : `produit`, `branche`, `date_validite`, `source`, `version_corpus`
- Le filtrage sur métadonnées avant la recherche vectorielle réduit l'espace de recherche et améliore la précision

---

# Schéma de table vectorielle recommandé (schéma ASCII)

```
┌──────────────────────────────────────────────────────────┐
│                    chunks_vectorises                     │
├─────────────────┬────────────────────────────────────────┤
│ chunk_id        │ UUID — clé primaire                    │
│ doc_id          │ FK → documents.id                      │
│ texte_chunk     │ TEXT — contenu original du passage     │
│ embedding       │ VECTOR(768) — vecteur d'embedding      │
│ produit         │ VARCHAR — ex. "RC Auto", "Prévoyance"  │
│ branche         │ VARCHAR — ex. "IARD", "Vie"            │
│ date_validite   │ DATE — date de validité du document    │
│ version_corpus  │ INT — numéro de version du corpus      │
│ created_at      │ TIMESTAMP — date d'ingestion           │
└─────────────────┴────────────────────────────────────────┘
```

---

# Filtrage par métadonnées — concept et exemples actuariels

- Le **pre-filtering** réduit l'index avant la recherche vectorielle : plus rapide, plus précis
- Le **post-filtering** applique les filtres sur les k résultats retournés : risque de résultats vides
- Exemple 1 : "clauses d'exclusion RC Auto valides en 2024" → filtre `produit = 'RC Auto' AND date_validite <= '2024-12-31'`
- Exemple 2 : "jurisprudence corporelle branche IARD" → filtre `branche = 'IARD'` avant la recherche
- Recommandation : indexer les colonnes de filtrage avec des index B-tree classiques (SQL)

---

# Gestion des versions du corpus

- Un corpus évolue : nouvelles circulaires, révisions tarifaires, mises à jour réglementaires (Solvabilité II)
- Stratégie 1 : **versioning par colonne** — `version_corpus` incrémentée, ancien contenu conservé
- Stratégie 2 : **snapshot complet** — nouvelle table `chunks_v2` créée à chaque grande mise à jour
- Traçabilité : chaque chunk doit référencer son document source, sa date d'ingestion et sa version de modèle d'embedding
- Règle d'or : ne jamais modifier un vecteur existant en place — toujours insérer une nouvelle ligne

---

# Mise à jour incrémentale du corpus

- La re-vectorisation complète d'un corpus de 5 M documents coûte plusieurs heures de calcul GPU
- Stratégie incrémentale : détecter les documents nouveaux ou modifiés (hash MD5 ou `updated_at`)
- Supprimer les chunks orphelins des documents supprimés ou remplacés
- Vectoriser uniquement les nouveaux chunks et les insérer dans l'index
- Planifier une re-indexation complète mensuelle pour corriger la dérive de l'index HNSW

---

# Monitoring de la base vectorielle

- **Qualité de recherche** : mesurer le recall@k sur un gold set de questions/réponses métier
- **Performance** : p50/p95 de latence de requête, débit (requêtes/seconde)
- **Volume** : croissance du nombre de chunks, taille de l'index sur disque
- **Freshness** : délai entre la parution d'un document et sa disponibilité dans l'index
- Alertes à définir : recall@5 < 80 %, latence p95 > 500 ms, index non mis à jour depuis > 48 h

---

# Ce qu'on retient — Stockage vectoriel

- Choisir la solution selon l'infrastructure existante : SQL Server ou pgvector en priorité pour Groupama
- L'index vectoriel est un compromis recall/vitesse — HNSW pour 100 k–1 M vecteurs, IVF au-delà
- Les métadonnées sont aussi importantes que les vecteurs : elles permettent le filtrage métier
- Versionner le corpus et tracer chaque chunk (source, date, modèle d'embedding)
- Surveiller le recall sur un gold set métier — la dérive silencieuse est le principal risque en production

---

<!-- _class: lead -->
# Jour 2 — Après-midi
## Recherche sémantique et prompting RAG

---

# Recherche et retrieval

- Le retrieval est le **maillon critique** du pipeline RAG : un mauvais retrieval ne peut pas être corrigé par le LLM
- Deux familles principales : **full-text search** et **recherche sémantique**
- Des mécanismes complémentaires : hybride, re-ranking, filtrage, déduplication
- L'évaluation du retrieval est indispensable avant de toucher au prompting
- Objectif de la session : comprendre chaque brique et savoir quand l'utiliser

---

# Full-text search vs recherche sémantique

| Critère | Full-text (BM25) | Sémantique |
|---|---|---|
| Principe | Correspondance de mots exacts | Proximité de sens |
| "sinistre auto" → "accident voiture" | ❌ Non trouvé | ✅ Trouvé |
| Requête avec fautes d'orthographe | ❌ Sensible | ✅ Tolérant |
| Requête longue en langage naturel | ⚠️ Partiel | ✅ Adapté |
| Vitesse | ⚡ Très rapide | 🐢 Plus lent |

---

# Full-text search — principe (BM25, TF-IDF)

- **TF-IDF** : score d'un terme = fréquence dans le document × rareté dans le corpus
  - Un mot fréquent partout ("le", "est") a un poids faible
  - Un mot rare et présent ("IBNR", "coassurance") a un poids fort
- **BM25** : amélioration de TF-IDF — sature la fréquence et normalise par la longueur du document
- Utilisé par Elasticsearch, Solr, la plupart des moteurs de recherche textuels
- Très efficace pour les **termes techniques métier** présents tels quels dans les documents
- Limite : "sinistre grave" et "accident sérieux" = 0 overlap → score nul

---

# Recherche sémantique — principe

- Les textes sont convertis en **vecteurs d'embedding** (ex. : dimension 768 ou 1536)
- La requête est elle aussi encodée en vecteur
- On calcule la **similarité cosinus** entre le vecteur-requête et chaque chunk indexé
- Les chunks les plus proches géométriquement = les plus proches sémantiquement
- "sinistre auto" et "accident voiture" → vecteurs voisins → retrouvés ensemble
- Modèles : `text-embedding-ada-002` (OpenAI), `e5-large`, `camembert` (français)

```
Requête : "calcul de la provision IBNR"
         ↓ embedding
    [0.12, -0.34, 0.87, ...]   ← vecteur de dimension 1536
         ↓ nearest neighbor search
    Top-5 chunks les plus proches dans l'index
```

---

# Quand utiliser full-text vs sémantique ?

| Situation | Recommandation |
|---|---|
| Recherche d'un identifiant exact (N° police, code produit) | Full-text |
| Termes techniques normalisés ("PSAP", "coassurance") | Full-text |
| Questions en langage naturel des utilisateurs | Sémantique |
| Synonymes métier, reformulations | Sémantique |
| Fautes de frappe, variantes orthographiques | Sémantique |
| Documents multilingues ou traduits | Sémantique |
| Recherche dans les titres et champs courts | Full-text |

> En pratique : combiner les deux (recherche hybride) donne les meilleurs résultats

---

# Recherche hybride — combiner les deux

- Exécuter en parallèle une recherche BM25 et une recherche vectorielle
- Fusionner les deux listes de résultats avec **RRF (Reciprocal Rank Fusion)**
  - Score RRF = Σ 1 / (k + rang_i) pour chaque liste
  - Pas de normalisation des scores entre les deux systèmes : seuls les rangs comptent
- Implémentations natives : Elasticsearch 8+, OpenSearch, Weaviate, Qdrant

```
BM25 results :   [chunk_A (1), chunk_C (2), chunk_F (3), ...]
Vector results : [chunk_B (1), chunk_A (2), chunk_D (3), ...]
                           ↓ RRF fusion
Hybrid results : [chunk_A, chunk_B, chunk_C, chunk_D, ...]
```

- Gain typique : +5 à +15 % de recall@5 par rapport à chaque méthode seule

---

# Top-k retrieval — principe

- Après le calcul de similarité, on ne garde que les **k chunks les plus proches**
- Ces k chunks forment le **contexte injecté dans le prompt**
- La valeur de k détermine :
  - La quantité d'information disponible pour le LLM
  - Le coût (tokens facturés) et la latence
  - Le risque de "dilution" du contexte si k est trop grand
- Top-k est le mode le plus courant, mais il existe des variantes :
  - **Score threshold** : garder tous les chunks au-dessus d'un seuil de similarité
  - **Top-k + threshold** : top-k avec un score minimum

---

# Top-k — comment choisir k ?

| Valeur de k | Avantages | Risques |
|---|---|---|
| k = 3 | Contexte concentré, prompt court | Recall insuffisant si la réponse est étalée |
| k = 5 | Bon compromis général | — |
| k = 10 | Haute couverture | Prompt long, coût élevé, dilution |
| k > 20 | Quasi-exhaustif | LLM "perdu" dans le contexte, hallucinations |

- **Règle pratique** : commencer à k = 5, évaluer le recall@5 sur un gold set
- Augmenter k si trop de questions sans réponse, réduire si trop de hallucinations
- En contexte actuariel : k = 5–8 souvent optimal pour des notes techniques de 20–50 pages

---

# Re-ranking — définition

- Le retrieval initial (BM25 ou vecteur) optimise la **couverture** (recall)
- Le re-ranking optimise la **précision** : reclasser les top-k pour mettre les chunks vraiment pertinents en tête
- Deux étapes :
  1. **Retrieval large** : récupérer top-50 ou top-100 candidats rapidement
  2. **Re-ranking fin** : scorer chaque candidat par rapport à la requête, garder top-5
- Le re-ranker voit la paire (requête, chunk) ensemble — il peut évaluer la pertinence réelle
- Coût supplémentaire : +50–200 ms de latence selon le modèle

---

# Re-ranking avec cross-encoders

- Un **bi-encoder** encode requête et chunk séparément → comparaison rapide mais approximative
- Un **cross-encoder** encode la paire (requête + chunk) conjointement → score plus précis
- Modèles open-source : `cross-encoder/ms-marco-MiniLM-L-6-v2`, `bge-reranker-base`
- APIs managées : Cohere Rerank, Jina Reranker

```
Bi-encoder :   embed(requête) · embed(chunk)  → score approximatif
Cross-encoder: encode(requête [SEP] chunk)    → score précis
```

- Le cross-encoder est 10–100× plus lent que le bi-encoder → réservé au re-ranking final
- Pipeline optimal : bi-encoder top-50 → cross-encoder top-5

---

# Re-ranking — amélioration mesurable de la précision

| Pipeline | Precision@5 (exemple) |
|---|---|
| BM25 seul | 52 % |
| Vecteur seul | 61 % |
| Hybride RRF | 68 % |
| Hybride + re-ranking | 79 % |

- Chiffres indicatifs — varient selon le corpus et les requêtes
- En actuariat : le re-ranking est particulièrement utile quand les documents contiennent beaucoup de tableaux chiffrés avec peu de contexte textuel
- Investissement : latence +100–300 ms, coût API marginal (Cohere ~0,001 $/1000 docs)

---

# Filtrage par métadonnées — exemples actuariels

- Les métadonnées permettent de restreindre la recherche **avant** ou **après** le calcul de similarité
- Exemples de filtres pertinents en actuariat :

| Métadonnée | Filtre possible |
|---|---|
| `type_document` | "note_technique", "rapport_audit", "procedure" |
| `branche` | "auto", "habitation", "santé", "vie" |
| `annee` | 2022, 2023, 2024 |
| `auteur` | service actuariat, direction technique |
| `langue` | "fr", "en" |

- Pré-filtrage : réduire l'espace de recherche → plus rapide, moins de bruit
- Post-filtrage : filtrer les résultats après retrieval → plus flexible mais moins efficace

---

# Combinaison filtrage + recherche vectorielle

- La combinaison optimale : **filtre dur** (métadonnées) + **tri souple** (similarité)
- Exemple de requête : "provisions IBNR branche auto, documents 2023-2024"

```
Étape 1 — Filtre dur :
  branche = "auto"  AND  annee IN [2023, 2024]
  → réduit le corpus de 50 000 à 1 200 chunks

Étape 2 — Recherche vectorielle :
  top-5 par similarité cosinus sur les 1 200 chunks filtrés
```

- Résultat : résultats précis, rapides, sans bruit inter-branches
- Attention : un filtre trop strict peut éliminer des chunks utiles → prévoir un fallback sans filtre

---

# La fenêtre de contexte — contrainte et gestion

- Les LLM ont une **fenêtre de contexte maximale** (tokens en entrée + sortie)
  - GPT-4o : 128 k tokens, Claude 3.5 Sonnet : 200 k tokens, Gemini 1.5 : 1 M tokens
- En pratique : même avec 128 k tokens, injecter tout le corpus = coût élevé + dégradation de qualité
- Le phénomène **"lost in the middle"** : le LLM se souvient mieux du début et de la fin du contexte
- Règle empirique : limiter le contexte RAG à **3 000–8 000 tokens** (≈ 5–10 chunks de 512 tokens)
- Stratégies de gestion :
  - Trier les chunks par score décroissant, garder les meilleurs
  - Placer les chunks les plus importants en début et fin de contexte
  - Compresser les chunks redondants

---

# Sélection et déduplication des chunks

- Le retrieval peut ramener plusieurs fois le même contenu (chunks chevauchants, paraphrase)
- Injecter des doublons = gaspillage de tokens + confusion du LLM
- Stratégies de déduplication :

| Méthode | Description |
|---|---|
| Hash exact | Supprimer les chunks identiques au caractère près |
| Similarité cosinus > 0.95 | Supprimer les quasi-doublons sémantiques |
| Même source + window adjacente | Fusionner les chunks contigus du même document |
| MMR | Sélectionner des chunks à la fois pertinents ET divers |

- En pratique : appliquer d'abord le hash exact, puis MMR pour la diversité

---

# MMR (Maximal Marginal Relevance) — diversité des résultats

- Problème : top-k peut renvoyer 5 chunks très similaires d'un même paragraphe
- **MMR** choisit itérativement les chunks qui maximisent la pertinence ET la diversité

```
Score MMR(chunk) = λ × sim(chunk, requête)
                 - (1-λ) × max sim(chunk, chunks_déjà_sélectionnés)
```

- λ = 1 → pure pertinence (= top-k classique)
- λ = 0 → pure diversité
- λ = 0.5–0.7 → bon compromis en pratique
- Cas d'usage actuariel : requête sur "méthodes de provisionnement" → éviter 5 chunks du même chapitre, obtenir une vue couvrant Chain-Ladder, Bornhuetter-Ferguson, et Cape Cod

---

# Évaluation du retrieval — métriques (Recall@k, Precision@k)

- Avant d'évaluer le LLM, évaluer le retrieval seul sur un **gold set** de paires (question, chunk_attendu)

| Métrique | Formule | Interprétation |
|---|---|---|
| Recall@k | chunks_attendus trouvés dans top-k / total chunks attendus | "Est-ce que la réponse est quelque part dans le contexte ?" |
| Precision@k | chunks_pertinents dans top-k / k | "Les chunks renvoyés sont-ils utiles ?" |
| MRR | 1 / rang du premier chunk pertinent | "Le chunk le plus utile est-il en tête ?" |
| NDCG@k | Weighted ranking by relevance score | Tient compte de l'ordre des résultats |

- **Recall@5 ≥ 80 %** est un seuil minimal acceptable pour un système en production

---

# Évaluation du retrieval — méthodes pratiques

- **Construire le gold set** : 50–200 questions métier avec les chunks attendus identifiés manuellement
- **Automatiser avec un LLM** : générer des questions synthétiques depuis les chunks existants (RAGAs, ARES)
- Processus d'évaluation :

```
Gold set : [(question_1, [chunk_A, chunk_B]), (question_2, [chunk_C]), ...]
               ↓
Pour chaque question → lancer le retrieval → comparer top-k aux chunks attendus
               ↓
Calculer Recall@5, Precision@5, MRR sur l'ensemble du gold set
               ↓
Itérer : ajuster k, chunking strategy, modèle d'embedding
```

- Rejouer le gold set à chaque changement de pipeline (regression testing)

---

# Cas d'usage actuariel — retrieval sur données hétérogènes

- Corpus typique Groupama : notes techniques (PDF), circulaires (Word), tableaux Excel, extraits de bases Access
- Défi : chaque format a ses particularités de retrieval

| Type de document | Stratégie recommandée |
|---|---|
| Notes techniques PDF (texte dense) | Chunking sémantique + vecteur |
| Tableaux de sinistres (CSV/Excel) | Métadonnées + full-text sur entêtes |
| Circulaires réglementaires | Full-text BM25 (termes précis) + date filter |
| Emails et comptes-rendus | Chunking court (256 tokens) + hybride |
| Données PSAP/IBNR structurées | SQL/filtrage direct, pas de RAG |

- Règle : ne pas vectoriser ce qui est mieux servi par une requête SQL structurée

---

# Bonnes pratiques de retrieval

- **Tester d'abord BM25** — souvent suffisant pour les termes techniques normalisés
- **Passer à l'hybride** si les utilisateurs posent des questions en langage naturel
- **Ajouter le re-ranking** si Precision@5 < 70 % malgré un bon Recall@5
- **Enrichir les métadonnées** dès l'ingestion — impossible à rattraper après
- **Monitorer le gold set** en continu — un recall qui baisse indique une dérive du corpus
- **Ne pas sur-optimiser k** — k = 5 est le bon point de départ dans 80 % des cas
- **Journaliser les requêtes et résultats** — source d'amélioration continue (feedback loop)
- **Séparer les index par domaine** si les branches métier ont des vocabulaires très différents

---

# Ce qu'on retient — Recherche et retrieval

- Full-text (BM25) pour les termes exacts, sémantique pour le sens — **hybride par défaut**
- Top-k : commencer à k = 5, ajuster selon le recall mesuré sur un gold set
- Le re-ranking (cross-encoder) améliore la précision de ~15 % pour un coût marginal
- Les métadonnées sont des **filtres durs** : les définir dès l'ingestion
- MMR évite la redondance dans le contexte injecté
- **Recall@5 ≥ 80 %** est le seuil minimal avant de travailler sur le prompting
- En actuariat : ne pas vectoriser ce qui est mieux servi par SQL ou full-text

---

<!-- _class: lead -->
# Prompting et qualité des réponses RAG

---

# Le prompt dans un système RAG — rôle et structure

- Le prompt est le **point de jonction** entre le retrieval et la génération
- Il transmet au LLM : son rôle, le contexte récupéré, la question de l'utilisateur
- Un prompt mal construit annule les bénéfices d'un retrieval parfait
- Trois responsabilités du prompt RAG :
  - **Cadrer** le comportement du modèle (ton, domaine, limites)
  - **Injecter** les chunks pertinents sans dépasser la fenêtre de contexte
  - **Contraindre** la réponse à rester fidèle aux sources

| Composant | Rôle |
|-----------|------|
| System prompt | Définit l'identité et les règles du modèle |
| Contexte | Les chunks récupérés par le retriever |
| Question | La requête utilisateur reformulée ou brute |

---

# Anatomie du prompt RAG (SYSTEM / CONTEXT / QUESTION)

```
[SYSTEM]
Tu es un assistant actuariel. Réponds uniquement à partir des documents fournis.
Si l'information n'est pas dans le contexte, dis-le explicitement.

[CONTEXT]
Document 1 (rapport Q3 2024, p.12) :
"Le ratio combiné s'établit à 98,2%..."
Document 2 (note technique, 2024-01) :
"La cadence des règlements montre..."

[QUESTION]
Quelle est l'évolution du ratio combiné sur les 3 derniers trimestres ?
```

- Chaque section a un rôle **précis et non interchangeable**
- L'ordre SYSTEM → CONTEXT → QUESTION est une convention éprouvée
- Les balises textuelles (`[SYSTEM]`, `[CONTEXT]`) aident le modèle à distinguer les sections

---

# Le prompt système — bonnes pratiques

- Définir **qui est le modèle** : rôle métier, domaine de compétence
- Énoncer les **règles de réponse** : ton, langue, format attendu
- Poser les **limites explicites** : ne pas inventer, ne pas sortir du contexte
- Rester **concis** : un system prompt trop long dilue les instructions critiques

| Bonne pratique | Exemple actuariel |
|----------------|-------------------|
| Définir le rôle | "Tu es un assistant spécialisé en actuariat IARD" |
| Langue fixe | "Réponds toujours en français" |
| Périmètre | "Tes réponses portent uniquement sur les données Groupama" |
| Limite d'invention | "Ne complète jamais par des données que tu n'as pas reçues" |

> Tester le system prompt seul avant d'ajouter le contexte — les bugs de comportement viennent souvent de là

---

# Injecter le contexte dans le prompt

- Chaque chunk est précédé d'un **en-tête de source** : document, page, date
- Les chunks sont séparés par un délimiteur visuel clair (`---` ou `###`)
- L'ordre d'injection influence le modèle : **placer les chunks les plus pertinents en premier**
- Respecter la **fenêtre de contexte** : tronquer proprement, ne pas couper une phrase

```
[CONTEXT]

### Source : Rapport annuel 2023 — p. 47
"Les provisions pour sinistres à payer (PSAP) s'élèvent à 1,2 Md€..."

### Source : Note de cadrage IARD — 2024-03
"Le ratio sinistres à primes bruts s'établit à 72,4% en cumul annuel..."
```

- Ne jamais injecter des chunks non pertinents pour "faire bonne mesure"
- Supprimer les redondances entre chunks avant injection (MMR, déduplication)

---

# Grounding — ancrer la réponse dans les sources

- Le **grounding** consiste à lier chaque affirmation de la réponse à un passage source
- Objectif : rendre la réponse **vérifiable** et **auditabl**e
- Trois niveaux de grounding :

| Niveau | Description | Usage |
|--------|-------------|-------|
| Implicite | Réponse cohérente avec le contexte, sans citation | Conversations rapides |
| Référence | Mention du document source en fin de réponse | Rapports internes |
| Inline | Citation exacte intégrée dans la réponse | Audit, compliance |

- En contexte actuariel : le grounding est **non négociable** pour les décisions de provisionnement
- Exiger le grounding dans le system prompt ou comme instruction finale

---

# Citations des sources — imposer la traçabilité

- Instruction explicite : *"Chaque affirmation doit être suivie de sa source entre crochets"*
- Format recommandé : `[Rapport Q3 2024, p.12]` ou `[Source 2]`
- Le modèle doit **numéroter les sources** dans l'en-tête de contexte pour pouvoir les référencer

```
Instruction de citation dans le prompt :
"Pour chaque fait avancé, indique entre crochets le numéro
 de la source correspondante. Si plusieurs sources confirment
 le même fait, cite-les toutes."
```

- Avantages :
  - Traçabilité pour la validation actuarielle
  - Détection facile des réponses non sourcées
  - Base pour l'évaluation automatique (faithfulness)
- Risque : le modèle peut citer des sources de manière incorrecte — **vérifier par échantillonnage**

---

# Techniques pour réduire les hallucinations

- Les hallucinations RAG sont différentes des hallucinations LLM pur : elles viennent du **manque ou de la mauvaise utilisation du contexte**

| Technique | Mécanisme |
|-----------|-----------|
| Instruction "hors contexte" | Forcer l'aveu d'ignorance si l'info est absente |
| Temperature basse | Réduire la créativité du modèle (0.0 – 0.2) |
| Citations obligatoires | Rendre chaque affirmation vérifiable |
| Contexte riche | Améliorer le recall pour donner plus à citer |
| Re-ranking | S'assurer que les meilleurs chunks sont en tête |

- En actuariat : la hallucination d'un ratio combiné ou d'un montant de provision est un **risque opérationnel réel**
- Tester systématiquement sur des questions dont la réponse n'est **pas dans le corpus**

---

# Instruction "si l'information n'est pas dans le contexte"

- Instruction indispensable dans tout prompt RAG métier
- Sans elle, le modèle complète avec ses connaissances générales — **invisible et dangereux**

```
Formulations recommandées :

1. "Si l'information demandée n'est pas présente dans
   les documents fournis, réponds : 'Je ne dispose pas
   de cette information dans les documents fournis.'"

2. "Ne réponds qu'à partir du contexte ci-dessus.
   Si la réponse n'y figure pas, dis-le explicitement
   plutôt que d'extrapoler."
```

- Cette instruction doit être **en fin de system prompt** (poids d'attention plus élevé)
- La tester avec des questions volontairement hors-corpus
- Mesurer le taux de refus correct — c'est un **indicateur de sécurité** du système

---

# Chain-of-Thought dans le RAG

- Le **Chain-of-Thought (CoT)** demande au modèle de raisonner étape par étape avant de conclure
- Utile quand la réponse exige de **croiser plusieurs chunks** ou de faire un calcul

```
Instruction CoT dans le prompt :
"Avant de donner ta réponse finale, analyse chaque
 document source disponible et indique ce qu'il apporte
 à la question. Ensuite seulement, formule ta conclusion."
```

- Avantages pour l'actuariat :
  - Permet de suivre le raisonnement sur des calculs de ratio
  - Révèle quels chunks ont été utilisés (ou ignorés)
  - Facilite la détection d'erreurs de logique

- Inconvénient : réponses plus longues — **adapter la limite de tokens** en conséquence
- Ne pas utiliser en production pour des requêtes simples (sur-coût inutile)

---

# Few-shot prompting dans le RAG

- Le **few-shot** consiste à fournir des exemples de questions/réponses dans le prompt
- Il calibre le **format**, le **ton** et le **niveau de détail** attendus

```
[EXEMPLES]

Q : Quel est le ratio combiné du T2 2024 ?
R : D'après le rapport Q2 2024 (p. 8), le ratio combiné
    s'établit à 97,4%, en amélioration de 1,2 point
    par rapport au T2 2023. [Source : Rapport Q2 2024, p.8]

Q : Quelle est la tendance des PSAP sur l'exercice ?
R : La note technique de mars 2024 indique une hausse
    des PSAP de 3,1% en cumul annuel. [Source : Note 2024-03]
```

- 2 à 3 exemples suffisent — au-delà, le contexte utile est compressé
- Les exemples doivent **respecter les règles de citation** définies dans le system prompt
- Idéal pour standardiser les réponses dans un outil métier partagé

---

# Gestion de la longueur des réponses

- Définir la longueur attendue dans le prompt réduit la variance des réponses

| Format | Instruction | Usage |
|--------|-------------|-------|
| Réponse courte | "Réponds en 2-3 phrases maximum" | Chatbot rapide |
| Synthèse | "Fournis une synthèse en moins de 150 mots" | Dashboard |
| Rapport | "Rédige une analyse structurée en 4 paragraphes" | Rapport métier |
| Bullet points | "Liste les points clés sous forme de puces" | Revue de direction |

- Recommandations :
  - Fixer une **limite de mots ou de tokens** selon l'interface cible
  - Séparer les questions simples des questions d'analyse — prompts différents
  - En actuariat : les notes techniques exigent de la précision, pas de la concision

---

# Réponses structurées (listes, tableaux)

- Le LLM peut structurer sa réponse selon des formats précis si on le lui demande
- Utile pour l'intégration dans des outils ou des rapports

```
Instructions de format dans le prompt :

"Présente ta réponse sous forme d'un tableau Markdown
 avec les colonnes : Indicateur | Valeur | Source | Période"

"Structure ta réponse ainsi :
  - CONSTAT : ...
  - ÉVOLUTION : ...
  - SOURCE : ..."
```

- Avantages :
  - Facilite le parsing programmatique de la réponse
  - Homogénéise les sorties dans un outil multi-utilisateurs
  - Améliore la lisibilité pour les métiers (tableaux de bord actuariels)

- Attention : la structure ne doit pas **forcer le modèle à inventer** des données pour remplir les colonnes

---

# Évaluation de la pertinence — métriques

- Un système RAG doit être évalué sur **deux dimensions indépendantes** : retrieval et génération

| Dimension | Métrique | Question posée |
|-----------|----------|----------------|
| Retrieval | Recall@k | Les bons chunks sont-ils retrouvés ? |
| Retrieval | Precision@k | Les chunks retournés sont-ils pertinents ? |
| Génération | Faithfulness | La réponse est-elle fidèle au contexte ? |
| Génération | Answer Relevance | La réponse répond-elle à la question ? |
| Global | Context Recall | Le contexte couvre-t-il la bonne information ? |
| Global | End-to-end | La réponse finale est-elle correcte et utile ? |

- Créer un **gold set** : questions avec réponses de référence et chunks attendus
- Mesurer régulièrement — les métriques évoluent quand le corpus change
- En actuariat : le gold set doit couvrir les cas limites (provisions insuffisantes, données manquantes)

---

# RAGAS — framework d'évaluation du RAG

- **RAGAS** (RAG Assessment) est un framework open-source d'évaluation automatisée
- Évalue le pipeline RAG sans annotation humaine extensive
- Quatre métriques principales calculées par un LLM juge :

| Métrique RAGAS | Ce qu'elle mesure | Plage |
|----------------|-------------------|-------|
| Faithfulness | Fidélité au contexte fourni | 0 – 1 |
| Answer Relevance | Pertinence par rapport à la question | 0 – 1 |
| Context Recall | Couverture de la bonne information | 0 – 1 |
| Context Precision | Proportion de contexte utile retourné | 0 – 1 |

- Nécessite uniquement : la question, le contexte récupéré, la réponse générée (et optionnellement la ground truth)
- Intégrable dans une **CI/CD** pour détecter les régressions
- Limite : le LLM juge peut lui-même halluciner — croiser avec évaluation humaine sur échantillon

---

# Faithfulness — la réponse est-elle fidèle au contexte ?

- La **faithfulness** mesure si chaque affirmation de la réponse est **supportée par le contexte**
- Calculée en décomposant la réponse en claims atomiques et en vérifiant chacun

```
Exemple de décomposition :

Réponse : "Le ratio combiné est de 98,2% et les PSAP
           ont augmenté de 3,1%."

Claims atomiques :
  1. Le ratio combiné est de 98,2%      → Vérifié dans Source 1 ✓
  2. Les PSAP ont augmenté de 3,1%      → Vérifié dans Source 2 ✓

Faithfulness = 2/2 = 1.0
```

- Seuil recommandé : **≥ 0,85** en production actuarielle
- Une faithfulness < 0,7 indique un problème de prompt ou de retrieval
- Causes fréquentes de score bas : contexte insuffisant, temperature trop haute, absence d'instruction "hors contexte"

---

# Answer Relevance — la réponse répond-elle à la question ?

- L'**answer relevance** mesure si la réponse est **directement utile** par rapport à la question posée
- Une réponse peut être fidèle au contexte mais passer à côté de la question

| Cas | Faithfulness | Answer Relevance |
|-----|-------------|-----------------|
| Réponse hors-sujet mais sourcée | Haute | Basse |
| Réponse pertinente mais inventée | Basse | Haute |
| Réponse correcte et sourcée | Haute | Haute |
| Réponse vague et générique | Moyenne | Basse |

- Calculée en générant des questions à partir de la réponse et en mesurant leur similarité avec la question originale
- Améliorer l'answer relevance : retravailler la formulation de la question, ajouter un step de **query rewriting**
- En actuariat : une réponse sur les provisions quand on demande le ratio sinistres = score bas

---

# Context Recall — les bons chunks ont-ils été retrouvés ?

- Le **context recall** mesure si les chunks récupérés contiennent l'information nécessaire pour répondre
- Nécessite une **ground truth** : la réponse de référence ou les chunks attendus

```
Calcul simplifié :

Ground truth claims : 4 affirmations attendues dans la réponse
Claims supportés par le contexte récupéré : 3

Context Recall = 3/4 = 0,75
```

- Un context recall bas signifie que le **retriever rate des informations clés**
- Actions correctives :

| Problème | Action |
|----------|--------|
| Recall global bas | Augmenter k, revoir le chunking |
| Recall sur termes exacts | Ajouter BM25 (recherche hybride) |
| Recall sur concepts | Améliorer les embeddings (fine-tuning) |
| Recall sur période | Enrichir les métadonnées temporelles |

---

# Évaluation humaine — quand et comment ?

- L'évaluation automatique (RAGAS) ne remplace pas le jugement humain sur les cas critiques
- L'évaluation humaine est indispensable pour :
  - Les décisions à fort impact (provisionnement, compliance)
  - La calibration initiale des métriques automatiques
  - La détection des biais non mesurés par les métriques

| Méthode | Description | Fréquence recommandée |
|---------|-------------|----------------------|
| Annotation en aveugle | Évaluateurs notent sans voir la source | Trimestrielle |
| A/B test | Comparaison de deux versions du système | À chaque changement majeur |
| Revue d'experts | Actuaires valident sur un échantillon métier | Mensuelle |
| Feedback implicite | Suivi des reformulations et des relances | Continue |

- Construire un **panel d'évaluateurs** incluant des actuaires et des utilisateurs finaux
- Documenter les désaccords — ils révèlent les cas ambigus à traiter dans le prompt

---

# Boucle d'amélioration continue du RAG

```
         ┌─────────────┐
         │   Requêtes  │
         │utilisateurs │
         └──────┬──────┘
                │
                ▼
    ┌───────────────────────┐
    │  Évaluation RAGAS     │
    │  + revue humaine      │
    └───────────┬───────────┘
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌───────────────┐ ┌──────────────────┐
│  Retrieval    │ │  Prompt / LLM    │
│  faible ?     │ │  faible ?        │
│               │ │                  │
│ → Chunking    │ │ → System prompt  │
│ → Embeddings  │ │ → Few-shot       │
│ → k / hybrid  │ │ → Temperature    │
└───────────────┘ └──────────────────┘
        │                │
        └───────┬────────┘
                ▼
    ┌───────────────────────┐
    │  Déploiement          │
    │  + gold set mis à jour│
    └───────────────────────┘
```

- Itérer sur le retrieval et le prompt **séparément** pour isoler les causes
- Mettre à jour le gold set à chaque évolution du corpus

---

# Cas d'usage : évaluation sur données actuarielles

- Scénario : système RAG sur les rapports de sinistres IARD Groupama

| Question de test | Attendu | Critère d'évaluation |
|-----------------|---------|----------------------|
| "Quel est le ratio combiné du T3 2024 ?" | 98,2% — Source : Rapport Q3 p.12 | Faithfulness + Answer Relevance |
| "Quelle est la tendance des PSAP sur 3 ans ?" | Synthèse multi-documents avec sources | Context Recall |
| "Quel est le taux de fréquence en auto ?" | "Information non disponible dans le contexte" | Refus correct |
| "Comparer les ratios sinistres 2022 vs 2023" | Tableau comparatif sourcé | Structure + Faithfulness |

- Résultats typiques observés sur un premier déploiement :
  - Faithfulness : 0,78 → après optimisation prompt : 0,91
  - Answer Relevance : 0,82 → après query rewriting : 0,88
  - Context Recall : 0,71 → après passage à k = 8 + hybride : 0,84

- L'amélioration du prompt seul peut gagner **+10 à +15 points** de faithfulness

---

# Ce qu'on retient — Prompting RAG

- Le prompt RAG = SYSTEM + CONTEXT + QUESTION — **chaque section a un rôle précis**
- Le system prompt définit les règles : rôle, langue, limites, format
- Toujours inclure l'instruction **"si l'information n'est pas dans le contexte"**
- Les citations de source sont obligatoires en contexte actuariel — **pas de réponse sans référence**
- Température basse (0.0 – 0.2) pour les systèmes de décision, plus haute pour la synthèse
- RAGAS automatise l'évaluation : Faithfulness ≥ 0,85, Answer Relevance ≥ 0,80, Context Recall ≥ 0,80
- L'évaluation humaine reste indispensable pour les cas à fort impact
- Améliorer le retrieval et le prompt **séparément** — toujours diagnostiquer avant d'itérer

---
