---
marp: true
theme: your-theme
paginate: true
title: "RAG pour données actuarielles — Jour 1"
header: "Conception d'un système RAG — Jour 1"
footer: "© Claude et Frédéric Gaurat 2026"
---

# Conception d'un système RAG
## pour l'exploitation de données actuarielles

### Jour 1 — Fondamentaux LLM & Ingestion de documents

**Durée** : 7h  |  **Prérequis** : Python, notions SQL  |  **Public** : Développeurs / Data analysts

---

# Programme — Jour 1

## Matin
- Histoire du NLP : de l'hypothèse distributionnelle au RAG
- Fondamentaux des LLM
- Architecture RAG : principes et démonstration

## Après-midi
- Ingestion et préparation de documents hétérogènes
- Stratégies de chunking

---

<!-- _class: lead -->
# Jour 1 — Matin
## Histoire du NLP : de l'hypothèse distributionnelle au RAG

---

# Histoire du NLP — De l'hypothèse distributionnelle au RAG

- 1954 : l'intuition fondatrice (Harris, Firth)
- 1965–1975 : Salton, TF-IDF et similarité cosinus
- 1980–2000 : modèles statistiques n-grammes
- 1990s : LSA, premiers vecteurs denses
- 2003 : Bengio, les réseaux de neurones entrent dans le texte
- 2013 : Word2Vec, le moment charnière
- 2017 : le Transformer, l'architecture qui change tout
- 2018 : BERT et GPT, la grande divergence
- 2020+ : ChatGPT, hallucinations, et la réponse RAG

---

# 1954 — L'hypothèse distributionnelle

- **Zellig Harris** (1954) : les mots apparaissant dans des contextes similaires ont des significations similaires
- **J.R. Firth** (1957) : *"You shall know a word by the company it keeps"*
- Idée révolutionnaire : apprendre le sens depuis les données, sans définition explicite
- Exemple : "zwingo" dans "boire un zwingo frais" / "commander un zwingo bien fruité" → on infère que c'est une boisson
- Ce principe est le fondement de Word2Vec, BERT, et de tous les embeddings modernes

> La co-occurrence dans un corpus suffit à apprendre quelque chose du sens

---

# 1965–1975 — Salton et le modèle vectoriel

- **Gerard Salton** (Cornell) développe le système **SMART** pour indexer des publications scientifiques
- Innovation clé : représenter un document comme un **vecteur** dans un espace à N dimensions
- Chaque dimension = un terme du vocabulaire
- La similarité entre deux documents = **cosinus de l'angle** entre leurs vecteurs
- **TF-IDF** : pondère les termes par leur fréquence dans le document × leur rareté dans le corpus

> Soixante ans plus tard, la similarité cosinus est toujours au cœur des bases vectorielles RAG

---

# TF-IDF — la formule fondatrice

- **TF** (Term Frequency) : fréquence d'un terme dans le document — plus il y est, plus il compte
- **IDF** (Inverse Document Frequency) : rareté du terme dans le corpus — les mots rares discriminent mieux
- "sinistre" dans un corpus d'assurance est peu discriminant (présent partout) ; "affaissement" l'est beaucoup plus
- Limite structurelle : deux documents traitant du même sujet avec des mots différents ont une similarité **nulle**
- "Voiture" et "automobile" sont aussi dissemblables que "voiture" et "probabilité" pour Salton

---

# 1980–2000 — Les modèles statistiques n-grammes

- Approche probabiliste née de la **reconnaissance vocale** (IBM, Bell Labs)
- Le prochain mot dépend des n-1 mots précédents : P(mot_t | mot_{t-2}, mot_{t-1})
- Probabilités apprises par comptage sur de grands corpus textuels
- Dominent la traduction automatique et la reconnaissance vocale jusqu'aux années 2010
- Limites : explosion combinatoire au-delà de 4-grammes, mots inconnus → probabilité nulle, toujours pas de sémantique

> Héritage direct : la notion même de "modèle de langue" — qu'un LLM comme Claude incarne à très grande échelle

---

# 1990s — LSA : le chaînon manquant

- **Deerwester et Dumais** (Bellcore, 1990) : appliquer la **décomposition en valeurs singulières** (SVD) à la matrice TF-IDF
- La SVD compresse 80 000 dimensions en ~300 dimensions latentes — analogue à une compression JPEG
- Pour la première fois : "voiture" et "automobile" deviennent **proches** dans l'espace compressé
- Les dimensions ne correspondent plus à des mots mais à des **concepts implicites** émergents
- Limite : méthode linéaire, ne distingue pas les sens d'un même mot ("banque" financière vs. fluviale)

> LSA est le pont intellectuel entre Salton et les embeddings neuronaux modernes

---

# 2003 — Bengio et l'entrée des réseaux de neurones

- **Yoshua Bengio** — *A Neural Probabilistic Language Model* (JMLR, 2003)
- Deux idées unifiées en un seul modèle entraîné de bout en bout :
  1. Une **table d'embeddings** : chaque mot → vecteur dense de 50 à 200 dimensions
  2. Un **réseau de neurones** qui prédit le mot suivant depuis ces embeddings
- Les embeddings ne sont pas construits manuellement — ils **émergent** de l'entraînement par rétropropagation
- Limite : trop coûteux à entraîner sur de grands corpus avec le matériel de l'époque

> Bengio pose les deux principes fondateurs des LLM — dix ans avant les GPU qui permettront de les réaliser à grande échelle

---

# 2013 — Word2Vec : le moment charnière

- **Tomas Mikolov** (Google) — *Efficient Estimation of Word Representations* (arXiv, jan. 2013)
- Innovation : **simplifier radicalement** le modèle de Bengio en supprimant les couches cachées
- Deux architectures légères : **CBOW** (contexte → mot) et **Skip-gram** (mot → contexte)
- Entraînable sur des **milliards de mots** en quelques jours sur un seul serveur
- Propriété spectaculaire :

```
vec(roi) − vec(homme) + vec(femme) ≈ vec(reine)
vec(Paris) − vec(France) + vec(Allemagne) ≈ vec(Berlin)
```

> Word2Vec est le moment où les embeddings passent du laboratoire à l'industrie

---

# 2014–2016 — Séquences, LSTM et attention

- **RNN** : traitement séquentiel — lit un token, met à jour un état caché, passe au suivant
- **LSTM** : ajoute des "portes" pour choisir quoi retenir ou oublier sur de longues séquences
- **seq2seq** (Sutskever, 2014) : encodeur LSTM → vecteur → décodeur LSTM — base de Google Traduction
- **Mécanisme d'attention** (Bahdanau, 2015) : le décodeur "regarde" tous les états de l'encodeur, pas juste le dernier
- Limite : traitement toujours séquentiel → peu parallélisable sur GPU, passage à l'échelle difficile

---

# 2017 — Le Transformer : l'architecture qui change tout

- **Vaswani et al.** (Google Brain) — *"Attention Is All You Need"* — 8 pages qui redéfinissent l'IA
- Supprime les RNN : **uniquement de l'attention**, appliquée en parallèle sur toute la séquence simultanément
- Chaque token pose une question (Query) aux autres (Keys) et reçoit une réponse pondérée (Values)
- **Multi-head attention** : plusieurs "têtes" capturent en parallèle syntaxe, coréférence, sémantique
- Conséquence décisive : **parallélisation complète** sur GPU → entraînable sur des centaines de milliards de tokens

> BERT, GPT, Llama, Mistral, Claude — toutes les architectures LLM modernes descendent de ces 8 pages

---

# 2018 — La grande divergence : BERT et GPT

Le Transformer propose encodeur + décodeur — deux équipes exploitent chacune une moitié :

| | BERT (Google, oct. 2018) | GPT (OpenAI, juin 2018) |
|---|---|---|
| Architecture | Encodeur uniquement | Décodeur uniquement |
| Lecture | Bidirectionnelle | Gauche → droite |
| Tâche | Prédire des mots masqués | Prédire le token suivant |
| Usage dans le RAG | **Vectoriser** les documents | **Générer** la réponse |

> Dans un pipeline RAG : un descendant de BERT encode, un descendant de GPT génère

---

# 2020–2022 — L'âge du gigantisme

- **GPT-3** (OpenAI, mai 2020) : 175 milliards de paramètres — 100× son prédécesseur
- **Capacités émergentes** : few-shot learning, raisonnement, code — sans entraînement supplémentaire
- **Lois d'échelle** (Kaplan, 2020) : la performance suit des lois de puissance prévisibles
- **ChatGPT** (nov. 2022) : 100 millions d'utilisateurs en 2 mois — l'IA générative entre dans le grand public
- Limitation structurelle qui émerge : données figées, pas d'accès aux connaissances privées, hallucinations

---

# Le problème structurel des LLM purs

- **Données figées** : connaissances bloquées à la date de coupure de l'entraînement
- **Pas de connaissances privées** : vos rapports, vos contrats internes n'existent pas pour le modèle
- **Hallucinations** : génère toujours une réponse plausible, même fausse, avec assurance totale
- Pour une équipe actuarielle : **100 % des données métier sont hors de portée d'un LLM seul**

> Ce trio de limitations a une seule réponse architecturale : le RAG

---

# 2020 — RAG : la synthèse de 60 ans de NLP

- **Patrick Lewis et al.** (Meta AI, 2020) — *Retrieval-Augmented Generation*
- Principe : avant de demander au LLM de répondre, **chercher** les passages pertinents et les lui fournir
- RAG recombine tous les héritages :
  - Cosinus de Salton → mesurer la similarité vectorielle
  - BM25 (descendant du TF-IDF) → recherche lexicale hybride
  - Embeddings (Bengio → Word2Vec → BERT) → espace sémantique dense
  - LLM (famille GPT) → synthétiser les passages en réponse cohérente

> Le RAG n'invente aucune brique — il les assemble en réponse à un besoin industriel précis

---

# Ce qu'on retient — Histoire du NLP

- Toute l'histoire du NLP est une succession de réponses aux limitations de la génération précédente
- TF-IDF et cosinus (Salton, 1965) → toujours au cœur des bases vectorielles modernes
- LSA → premier pont entre lexical et sémantique ; Bengio → embeddings appris end-to-end
- Word2Vec → les embeddings passent en industrie ; Transformer → la parallélisation rend le scaling possible
- BERT encode, GPT génère — le RAG les fait collaborer

> Comprendre cette généalogie, c'est comprendre *pourquoi* chaque composant du RAG est conçu comme il l'est

---

# État de l'art IA et fondamentaux des LLM

- Qu'est-ce qu'un LLM ?
- Tokenisation et génération de texte
- Panorama des modèles (propriétaires et open source)
- Quand utiliser un LLM vs d'autres approches ?
- Enjeux de confidentialité et souveraineté

---

# Qu'est-ce qu'un LLM ?

- **L**arge **L**anguage **M**odel : réseau de neurones entraîné sur des milliards de textes
- Prédit le token suivant à partir du contexte — pas de "compréhension" au sens humain
- Paramètres = poids appris : GPT-4 ≈ 1 000 milliards, Mistral 7B ≈ 7 milliards
- Capacités émergentes : résumé, traduction, extraction, génération de code
- Cas actuariel : synthétiser 500 pages de conditions générales en 10 lignes

> Un LLM est un compresseur de texte probabiliste, pas une base de données

---

# Tokenisation — définition et unité de base

- Un **token** est l'unité atomique traitée par le modèle (ni mot, ni caractère)
- Découpage basé sur la fréquence dans le corpus d'entraînement (algorithme BPE)
- Mots courants = 1 token ; mots rares ou techniques = plusieurs tokens
- Les nombres sont souvent découpés chiffre par chiffre : "2024" → 4 tokens
- Le vocabulaire d'un modèle contient typiquement 32 000 à 128 000 tokens

> Les LLM ne lisent pas du texte — ils traitent des séquences de nombres entiers

---

# Tokenisation — l'algorithme BPE

**Byte Pair Encoding** (Philip Gage, 1994) : construire un vocabulaire par fusions successives de paires fréquentes

1. **Initialisation** : vocabulaire = chaque caractère individuel
2. **Itération** : trouver la paire de tokens adjacente la plus fréquente → la fusionner en un seul nouveau token
3. **Arrêt** : quand le vocabulaire atteint la taille cible (GPT-4o : 200 019 tokens)

```
Mini-corpus : sinistre  sinistres  sinistralité

  Étape 1 → paire (s, i) très fréquente  →  nouveau token "si"
  Étape 2 → paire (si, n) fréquente      →  nouveau token "sin"
  Étape 3 → paire (n, i) fréquente       →  nouveau token "ni"
  …
  Résultat : sin|istre  ·  sin|istres  ·  sin|istr|alité
```

- Mots **fréquents dans le corpus** d'entraînement → peu de fragments
- Termes rares (`IBNR`, `Bornhuetter-Ferguson`) → beaucoup fragmentés
- GPT-4o entraîné sur corpus majoritairement anglophone → **le français se fragmente plus**

> BPE ne connaît pas le sens des mots — il optimise la compression statistique du corpus

---

# Tokenisation — en pratique

- "sinistre" → 1 token | "sinistralité" → 3 tokens | "IBNR" → 2-3 tokens
- "ratio combiné" → 3 tokens | "provisions pour sinistres à payer" → 7 tokens
- Les acronymes actuariels (PSAP, S/P, IARD) sont souvent mal découpés
- Le français est moins bien représenté que l'anglais dans la plupart des tokenizers
- Impact : un même contenu en français coûte 10-20 % plus cher qu'en anglais

> Tester son corpus sur platform.openai.com/tokenizer avant d'estimer les coûts

---

# Tokenisation — impact sur les coûts et les limites

- Coût API = nb de tokens en entrée × prix input + nb tokens en sortie × prix output
- Un rapport actuariel de 20 pages ≈ 8 000-12 000 tokens selon la densité
- La fenêtre de contexte est exprimée en tokens, pas en mots ni en pages
- Règle pratique : **1 token ≈ 0,75 mot** en français (0,85 en anglais)
- Calcul : 100 000 tokens input GPT-4o ≈ 0,25 $ (mai 2026)

> Sous-estimer les tokens = dépassement de budget ou troncature silencieuse du contexte

---

# Le mécanisme d'attention — intuition

- Problème : comment relier "le sinistre déclaré en 2022" à "il" trois phrases plus loin ?
- L'attention permet à chaque token de "regarder" tous les autres tokens du contexte
- Score d'attention = importance relative d'un token par rapport aux autres
- Analogie : lecture humaine — on relit le début d'un contrat pour comprendre une clause tardive
- C'est ce mécanisme qui différencie les Transformers des RNN séquentiels

> L'attention calcule, pour chaque mot, quels autres mots du contexte comptent le plus

---

# Le mécanisme d'attention — Self-attention et contexte

- **Self-attention** : chaque token s'interroge sur sa relation avec tous les autres tokens
- Trois vecteurs par token : Query (ce que je cherche), Key (ce que je suis), Value (ce que j'apporte)
- Score = produit scalaire Query × Key → softmax → somme pondérée des Values
- Multi-head attention : plusieurs "têtes" apprennent différents types de relations en parallèle
- Exemple : tête 1 capte la syntaxe, tête 2 capte la coréférence, tête 3 capte la temporalité

> Plus le contexte est long, plus le calcul d'attention est coûteux (O(n²) en mémoire)

---

# Les Transformers — architecture générale

- Architecture proposée par Vaswani et al. en 2017 ("Attention Is All You Need")
- Deux blocs principaux : **Encoder** (comprendre) et **Decoder** (générer)
- Les LLM modernes sont des Decoder-only : BERT est Encoder-only, T5 est Encoder-Decoder
- Chaque couche = Self-attention + Feed-Forward Network + normalisation résiduelle
- Les modèles empilent N couches identiques (GPT-3 : 96 couches, Mistral 7B : 32 couches)

```
Token → Embedding → [Attention + FFN] × N couches → Logits → Token suivant
```

---

# La génération de texte — génération autorégressive

- Le modèle génère **un token à la fois**, en boucle, jusqu'à un token spécial [EOS]
- À chaque étape : le token généré est ajouté au contexte pour prédire le suivant
- Le modèle produit une distribution de probabilité sur tout le vocabulaire à chaque pas
- Conséquence : la génération est non déterministe par défaut
- Exemple : générer un résumé de 200 mots = ≈ 270 appels internes au réseau

> La "fluidité" du texte généré est une illusion statistique, pas une pensée

---

# Température et sampling — contrôler la créativité

- **Température** : paramètre qui ajuste la distribution de probabilité des tokens
- Température = 0 → déterministe (toujours le token le plus probable)
- Température = 1 → distribution d'origine | Température > 1 → plus aléatoire
- **Top-p (nucleus sampling)** : ne considère que les tokens dont la somme de proba ≥ p
- **Top-k** : ne considère que les k tokens les plus probables

| Usage | Température conseillée |
|---|---|
| Extraction structurée (JSON, tableau) | 0 – 0.2 |
| Résumé factuel de rapport sinistres | 0.2 – 0.5 |
| Génération de commentaire narratif | 0.7 – 1.0 |

---

# La fenêtre de contexte — définition et contrainte

- La fenêtre de contexte = nombre maximum de tokens traités en une seule requête
- Elle inclut : le prompt système + l'historique + les documents + la réponse générée
- Modèles courants : GPT-4o → 128k tokens | Claude 3.5 → 200k tokens | Gemini → 1M tokens
- Au-delà de la fenêtre : troncature ou erreur — le modèle "oublie" le début
- Un corpus de 10 000 pages de sinistres ne tient pas dans une seule fenêtre

> La fenêtre de contexte est la principale raison d'être d'une architecture RAG

---

# Panorama des modèles — propriétaires vs open source

- **Propriétaires** : GPT (OpenAI), Claude (Anthropic), Gemini (Google), Command (Cohere)
- **Open source** : Llama (Meta), Mistral, DeepSeek, Falcon, Qwen (Alibaba)
- Critères de choix : performance, coût, confidentialité, latence, personnalisation
- Les modèles open source comblent rapidement l'écart de performance
- Tendance 2024-2026 : modèles spécialisés par domaine (finance, juridique, médical)

> Pour Groupama : les données de sinistres sont sensibles → la localisation du modèle compte

---

# GPT (OpenAI) — caractéristiques et usage

- Famille GPT-4 (2023) → GPT-4o (2024) → GPT-4.5 (2025) — modèle phare d'OpenAI
- Fenêtre de contexte : 128 000 tokens | Multimodal : texte, image, audio
- Forces : meilleure instruction-following du marché, écosystème riche, API mature
- Faiblesses : coût élevé, données envoyées aux serveurs US, dépendance fournisseur
- Usage actuariel : extraction de clauses, génération de synthèses, QA sur conditions générales

> API disponible via Azure OpenAI Service pour hébergement en zone européenne

---

# Claude (Anthropic) — caractéristiques et usage

- Famille Claude 3 (Haiku / Sonnet / Opus) → Claude 3.5 → Claude 4 (2025-2026)
- Fenêtre de contexte : 200 000 tokens — avantage pour les longs documents
- Forces : excellente compréhension de documents longs, instructions nuancées, moindre hallucination
- Faiblesses : API moins mature qu'OpenAI, écosystème d'outils plus restreint
- Usage actuariel : analyse de rapports actuariels multi-pages, revue de provisions

> Anthropic met en avant la sécurité et l'alignement — pertinent pour un contexte réglementé

---

# Mistral — modèle open source européen

- Créé par Mistral AI (Paris, 2023) — champion européen de l'IA open source
- Modèles : Mistral 7B, Mixtral 8×7B (MoE), Mistral Large, Mistral Small
- Fenêtre de contexte : 32k tokens (Mistral 7B) à 128k tokens (Mistral Large)
- Forces : performant pour sa taille, licence Apache 2.0, déployable sur site
- Faiblesses : moins performant que GPT-4o sur les tâches complexes de raisonnement

> Option souveraine : déploiement sur infrastructure française possible via la plateforme Le Chat ou en self-hosted

---

# Llama (Meta) — modèle open source

- Développé par Meta AI — Llama 2 (2023), Llama 3 (2024), Llama 3.1 (2024)
- Tailles disponibles : 8B, 13B, 70B, 405B paramètres (Llama 3.1)
- Fenêtre de contexte : 8k tokens (Llama 2) → 128k tokens (Llama 3.1)
- Forces : licence permissive pour usage commercial, très large communauté, nombreux fine-tunes
- Faiblesses : nécessite du matériel GPU pour les grandes versions, pas de support officiel

> Base de la plupart des modèles fine-tunés sectoriels (finance, santé, juridique)

---

# DeepSeek — modèle open source chinois

- Développé par DeepSeek AI (Hangzhou, Chine) — R1 et V3 publiés fin 2024 / début 2025
- Architecture MoE (Mixture of Experts) — efficacité computationnelle remarquable
- Performance proche de GPT-4o sur les benchmarks de raisonnement mathématique
- Forces : open source, coût d'inférence très faible, excellent en code et raisonnement
- Faiblesses : origine géographique soulève des questions de souveraineté des données

> À utiliser uniquement en mode self-hosted pour des données sensibles type sinistres

---

# Propriétaires vs Open Source

| Critère | Propriétaire | Open Source |
|---|---|---|
| Performance | ⭐⭐⭐ | ⭐⭐ à ⭐⭐⭐ |
| Coût | API payante | Hébergement propre |
| Confidentialité | Données envoyées en cloud | Exécution locale possible |
| Maintenance | Gérée par l'éditeur | À la charge de l'équipe |
| Personnalisation | Limitée (prompts) | Fine-tuning possible |
| Conformité RGPD | Dépend de la région | Maîtrisable si on-premise |

---

# Quand utiliser un LLM ? — cas d'usage adaptés

- **Synthèse documentaire** : résumer 50 rapports de sinistres en fiches structurées
- **Extraction d'information** : identifier montants, dates, clauses dans des contrats
- **Génération de commentaires** : narratifs automatiques pour le reporting actuariel
- **Question / Réponse** : interroger une base documentaire interne (→ RAG)
- **Classification** : catégoriser des sinistres par nature ou gravité à partir du texte

> Un LLM n'est pas adapté quand la réponse exacte est dans une base de données structurée

---

# LLM vs ML classique — tableau comparatif

| Critère | LLM | ML classique (XGBoost, RF…) |
|---|---|---|
| Type de données | Texte non structuré | Données tabulaires structurées |
| Entraînement | Pré-entraîné (fine-tune optionnel) | Entraînement sur données métier |
| Interprétabilité | Faible | Moyenne à bonne (SHAP) |
| Volume de données requis | Faible (few-shot) | Important |
| Prédiction de sinistres | Non adapté | Adapté (fréquence, sévérité) |
| Analyse de texte de contrat | Adapté | Non adapté |

---

# Enjeux de confidentialité et souveraineté des données

- Les données actuarielles sont soumises au RGPD et aux directives Solvabilité II
- Envoyer des sinistres nominatifs à une API cloud = risque de non-conformité
- Trois niveaux de risque : données publiques (faible) | données agrégées (moyen) | données individuelles (élevé)
- Stratégies : anonymisation avant envoi | modèle on-premise | API hébergée en UE
- Fournisseurs avec hébergement UE : Azure OpenAI (France Central), Mistral Le Chat, OVHcloud AI

> Règle interne Groupama à définir : quelles données peuvent sortir du SI ?

---

# Ce qu'on retient — Fondamentaux LLM

- Les LLM traitent des tokens, pas des mots — tout coût est exprimé en tokens
- L'attention permet au modèle de relier les éléments dans une fenêtre de contexte limitée
- Choix propriétaire vs open source = arbitrage performance / confidentialité / coût
- Un LLM seul n'est pas adapté pour exploiter un corpus documentaire interne → RAG
- Les données actuarielles sensibles imposent une réflexion sur la localisation du modèle

---

# Architecture RAG : principes et démonstration

- Le problème des hallucinations
- Architecture complète : ingestion → chunking → embedding → stockage → retrieval → génération
- RAG dans le contexte actuariel
- Avantages, limites et comparaison avec le fine-tuning

---

# Le problème des hallucinations

- Un LLM génère toujours une réponse plausible, même sans information fiable
- Il ne "sait" pas ce qu'il ne sait pas
- Sur des données métier internes : **100% des faits sont hors de sa connaissance**
- Les réponses sont confiantes, fluides… et potentiellement fausses

> Une hallucination dans un rapport actuariel peut entraîner des décisions de provisionnement erronées

---

# Hallucinations — exemples et conséquences

- **Exemple 1** : le modèle invente un ratio combiné à 94,3 % pour la branche MRH T3 2024 — chiffre inexistant
- **Exemple 2** : il cite une norme Solvabilité II avec un numéro d'article erroné
- **Exemple 3** : il confond la provision pour sinistres tardifs (IBNR) avec la provision mathématique
- Conséquence : décisions de provisionnement biaisées, risque de non-conformité réglementaire

> "Le modèle ne ment pas — il complète du texte de façon statistiquement cohérente, sans notion de vérité"

---

# Hallucinations — pourquoi ça arrive ?

- Le LLM est entraîné à **prédire le token suivant le plus probable**, pas à vérifier des faits
- Il n'a pas accès à vos bases internes ni à vos reportings — ils n'existent pas dans ses paramètres
- Sa "connaissance" est une compression statistique du texte d'entraînement (coupure en 2023-2024)
- Plus la question est spécifique et interne, plus le risque d'hallucination est élevé

> Règle pratique : plus une information est confidentielle / récente / propre à votre organisation, moins le LLM seul est fiable

---

# La solution : ancrer le LLM dans les faits

- Principe : fournir au LLM les **documents sources pertinents** dans son contexte au moment de la question
- Le modèle répond en s'appuyant sur ces extraits, pas sur sa mémoire paramétrique
- C'est le principe du **RAG** (Retrieval-Augmented Generation)
- Le LLM devient un "moteur de synthèse" plutôt qu'une source de connaissance

> RAG = Retrieval (recherche) + Augmented (contexte enrichi) + Generation (réponse du LLM)

---

# Vue d'ensemble du pipeline RAG

- **Phase offline (ingestion)** : préparer et indexer les documents une seule fois
- **Phase online (requête)** : récupérer les passages pertinents à la volée et les injecter dans le prompt
- Six étapes enchaînées : ingestion → chunking → embedding → stockage → retrieval → génération
- Chaque étape impacte la qualité finale des réponses

```
[Documents] → Ingestion → Chunking → Embedding → [Base vectorielle]
                                                         ↑
[Question]  → Embedding → Retrieval → Chunks → [LLM] → [Réponse]
```

---

# Étape 1 — Ingestion des documents

- Collecter les sources : PDF de rapports actuariels, Word de contrats, Excel de triangles de développement
- Extraire le texte brut en préservant la structure (titres, tableaux, métadonnées)
- Gérer les formats hétérogènes : PDF scannés (OCR requis), tableaux Excel, HTML de bases internes
- Nettoyer : retirer les en-têtes/pieds de page répétés, les artefacts d'export PDF

> La qualité de l'ingestion conditionne toute la chaîne — "garbage in, garbage out"

---

# Étape 2 — Découpage (chunking)

- Un document entier ne tient pas dans le contexte du LLM → le découper en **chunks** (fragments)
- Stratégies courantes : découpage par taille fixe (ex. 512 tokens), par paragraphe, par section logique
- **Overlap** : faire se chevaucher les chunks (ex. 50 tokens) pour ne pas couper le sens en deux
- Taille optimale : compromis entre précision du retrieval (petits chunks) et contexte suffisant (grands chunks)

> Un rapport de provisionnement de 80 pages devient ~400 chunks de 200 tokens avec 20 tokens de recouvrement

---

# Étape 3 — Vectorisation (embedding)

- Chaque chunk est transformé en un **vecteur numérique** (ex. 1 536 dimensions avec text-embedding-ada-002)
- Le vecteur capture la **sémantique** du texte : deux phrases proches sémantiquement ont des vecteurs proches
- Modèles d'embedding : OpenAI text-embedding-3, Mistral Embed, sentence-transformers (open source)
- Cette opération est réalisée **une seule fois** à l'ingestion — coût faible et résultat mis en cache

> "Ratio combiné élevé" et "sinistralité dégradée" auront des vecteurs proches même si les mots diffèrent

---

# Étape 4 — Stockage vectoriel

- Les vecteurs sont stockés dans une **base vectorielle** (vector store) optimisée pour la recherche par similarité
- Exemples de bases vectorielles : Chroma (local, open source), Pinecone (cloud), pgvector (PostgreSQL), Qdrant
- Chaque vecteur est associé aux **métadonnées** du chunk : source, page, date, branche d'assurance
- Les métadonnées permettent de filtrer la recherche (ex. "uniquement les rapports MRH 2024")

| Base | Hébergement | Open source | Cas d'usage |
|---|---|---|---|
| Chroma | Local | Oui | Prototypage, dev |
| pgvector | On-premise | Oui | SI existant PostgreSQL |
| Pinecone | Cloud | Non | Production scalable |
| Qdrant | Local / cloud | Oui | Production on-premise |

---

# Étape 5 — Retrieval (recherche sémantique)

- La question de l'utilisateur est vectorisée avec le **même modèle d'embedding** que les chunks
- On calcule la **similarité cosinus** entre le vecteur de la question et tous les vecteurs stockés
- Les k chunks les plus proches (ex. k=5) sont récupérés et transmis au LLM
- Améliorations possibles : re-ranking, filtrage par métadonnées, recherche hybride (sémantique + mots-clés)

> La question "provisions IBNR auto T4" retrouvera les chunks parlant de "sinistres tardifs automobile trimestre 4" même sans correspondance lexicale exacte

---

# Étape 6 — Génération augmentée

- Les chunks récupérés sont insérés dans le **prompt système** comme contexte documentaire
- Le LLM reçoit : [instructions] + [chunks pertinents] + [question utilisateur]
- Il génère une réponse **ancrée dans les extraits fournis**, avec possibilité de citer la source
- Le prompt peut imposer : "réponds uniquement à partir des documents fournis, sinon dis 'information non disponible'"

> Cette étape transforme le LLM : d'oracle potentiellement hallucinatoire → moteur de synthèse documentaire fiable

---

# Le pipeline RAG — vue d'ensemble

```
Documents PDF / Word / Excel
         ↓
    [Ingestion]
         ↓
     [Chunking]
         ↓
    [Embedding]
         ↓
 [Base vectorielle]
         ↑
Question → [Vectorisation] → [Retrieval] → Chunks pertinents
                                                  ↓
                               [LLM] → Réponse contextualisée
```

---

# RAG dans le contexte actuariel — cas d'usage

- **Requête sur les provisions** : "Quelle est la provision IBNR pour la branche RC Auto au T3 2024 ?" → RAG interroge les rapports de clôture
- **Analyse de contrats** : extraction automatique des clauses de franchise ou de plafond dans des polices PDF
- **Synthèse de triangles** : résumé narratif d'un triangle de développement issu d'un fichier Excel ingéré
- **Veille réglementaire** : questions sur les textes Solvabilité II ou IFRS 17 ingérés en base

> Le RAG ne remplace pas l'actuaire — il accélère l'accès à l'information et la rédaction de synthèses

---

# Avantages du RAG

- **Ancrage factuel** : les réponses sont vérifiables — chaque affirmation peut être tracée à un document source
- **Mise à jour facile** : ajouter un nouveau rapport = ré-ingestion d'un document, pas de ré-entraînement
- **Confidentialité** : les documents restent dans votre infrastructure — seuls les chunks pertinents transitent vers le LLM
- **Contrôle du périmètre** : le système répond "je ne sais pas" si l'information n'est pas dans la base

> Coût de mise en œuvre faible comparé au fine-tuning : pas besoin de données d'entraînement étiquetées

---

# Limites du RAG

- **Qualité de l'ingestion** : un PDF mal extrait ou un tableau Excel mal parsé dégrade toute la chaîne
- **Chunking sensible** : un mauvais découpage coupe le contexte et le retrieval retrouve des fragments incomplets
- **Latence** : l'étape de retrieval ajoute 100-500 ms par requête selon la taille de la base
- **Raisonnement complexe** : le RAG ne résout pas les problèmes nécessitant un raisonnement multi-étapes sur des données dispersées

> Limite critique : si l'information n'est pas dans la base ou mal indexée, le RAG ne peut pas la trouver — qualité documentaire indispensable

---

# RAG vs Fine-tuning — quand choisir quoi ?

| Critère | RAG | Fine-tuning |
|---|---|---|
| Corpus documentaire évolutif | Adapté (ré-ingestion simple) | Non adapté (ré-entraînement coûteux) |
| Données propriétaires confidentielles | Adapté (restent on-premise) | Risqué (dans les poids du modèle) |
| Style / ton spécifique à l'organisation | Limité | Adapté |
| Traçabilité des sources | Oui (citation du chunk) | Non |
| Coût de mise en œuvre | Faible à moyen | Élevé (données, GPU, expertise) |
| Réponses sur faits récents | Oui (mise à jour de la base) | Non (coupure à la date d'entraînement) |

> Règle pratique : RAG d'abord. Fine-tuning uniquement si le ton, le format ou le domaine très spécialisé l'exige.

---

# Démo conceptuelle — question sans RAG

**Question** : "Quel est le ratio de sinistralité de la branche MRH au T3 2024 ?"

**Réponse du LLM seul (sans RAG) :**

> "D'après les tendances du marché, le ratio de sinistralité MRH en France se situe généralement autour de 68-72 % pour les grands groupes d'assurance. Pour Groupama, on peut estimer un ratio proche de 70,4 % au T3 2024, en ligne avec la sinistralité climatique observée cet été."

- Le chiffre "70,4 %" est **inventé** — le modèle n'a pas accès aux reportings internes
- La réponse semble crédible, sourcée, précise → danger maximal
- Aucun avertissement sur l'absence de source réelle

---

# Démo conceptuelle — question avec RAG

**Question** : "Quel est le ratio de sinistralité de la branche MRH au T3 2024 ?"

**Réponse du LLM avec RAG (chunks du rapport de clôture T3 2024 récupérés) :**

> "Selon le rapport de clôture actuarielle Q3 2024 (page 14), le ratio de sinistralité de la branche MRH s'établit à **73,8 %**, en hausse de 2,1 points par rapport au T3 2023, principalement en raison des événements climatiques d'août 2024 (grêle Sud-Ouest)."

- Le chiffre provient d'un **document réel ingéré** dans la base vectorielle
- La source est **citée et traçable** (rapport, page)
- Le contexte causal (grêle) est extrait du même document
- Si le document n'était pas en base : "Information non disponible dans les sources indexées"

---

# Ce qu'on retient — Architecture RAG

- Les LLM hallucinent : ne jamais les utiliser sans ancrage documentaire pour des données métier
- Le RAG = pipeline en 6 étapes : ingestion → chunking → embedding → stockage → retrieval → génération
- Chaque étape a un impact sur la qualité finale des réponses
- Le RAG est préférable au fine-tuning pour des corpus qui évoluent souvent

---

<!-- _class: lead -->
# Jour 1 — Après-midi
## Ingestion et préparation de documents hétérogènes

---

# Ingestion et préparation de documents hétérogènes

- Les formats de documents dans un contexte actuariel
- Extraction depuis PDF (structurés et scannés)
- Lecture de documents Word et fichiers Excel
- Gestion des métadonnées et traçabilité des sources

---

# Les formats de documents dans un contexte actuariel

- **PDF** : rapports de clôture, notes actuarielles, études techniques, comptes-rendus ORSA
- **Word (.docx)** : modèles de rapports, procédures, annexes rédigées, courriers sinistres
- **Excel (.xlsx)** : triangles de développement, tableaux de bord, séries de primes, provisions Best Estimate
- **Images scannées** : archives papier numérisées, avenants signés, pièces justificatives sinistres
- Chaque format impose une stratégie d'extraction différente avant tout traitement RAG

---

# PDF structuré — définition et extraction de texte

- Un PDF structuré contient du texte lisible directement, sans passer par la reconnaissance optique
- C'est le format dominant pour les rapports actuariels, notes techniques et rapports ORSA
- La qualité du texte extrait dépend fortement du générateur du PDF (Word exporté vs impression virtuelle)
- Les mises en page complexes (colonnes, tableaux imbriqués) peuvent désorganiser l'ordre de lecture
- Toujours vérifier un échantillon d'extraction sur des pages représentatives avant traitement en masse

---

# PDF structuré — bibliothèques d'extraction

- **pypdf** : bibliothèque légère, idéale pour extraire le texte brut de PDF simples à structure linéaire
- **pdfplumber** : spécialisée dans l'extraction de tableaux et l'analyse de la mise en page (coordonnées)
- **pymupdf (fitz)** : très performante, gère les polices embarquées, les métadonnées et les annotations
- **camelot / tabula** : orientées extraction de tableaux tabulaires depuis des PDF (utile pour triangles de sinistres)
- Le choix dépend du type de document : texte pur → pypdf ; tableaux actuariels → pdfplumber ou camelot

> Toujours tester plusieurs bibliothèques sur un échantillon représentatif de votre corpus

---

# PDF scanné — le problème de l'OCR

- Un PDF scanné est une image : aucun texte n'est extractible sans reconnaissance optique de caractères (OCR)
- La qualité de la numérisation (résolution, contraste, inclinaison) détermine la qualité de l'OCR
- Erreurs typiques : confusion 0/O, 1/l/I, caractères accentués mal reconnus, sauts de ligne parasites
- Les tableaux de chiffres (triangles de développement, tableaux de provisions) sont particulièrement fragiles
- Un post-traitement de nettoyage est indispensable avant tout usage dans un pipeline RAG

---

# PDF scanné — approches OCR

- **Tesseract** : moteur OCR open-source de référence, supporte le français, intégrable dans tout pipeline local
- **pytesseract** : wrapper Python autour de Tesseract, utilisable avec une image PIL ou une page PDF convertie
- **Services cloud** : AWS Textract, Google Document AI, Azure Form Recognizer — précision supérieure, coût variable
- **Doctr / EasyOCR** : alternatives open-source modernes, meilleures sur les documents dégradés ou inclinés
- Pour des archives actuarielles sensibles : privilégier les solutions on-premise (Tesseract, Doctr) pour éviter l'exposition de données

> Les services cloud offrent une précision supérieure sur les tableaux mais exposent des données potentiellement confidentielles

---

# Pièges courants de l'extraction PDF

- **En-têtes et pieds de page** : répétés sur chaque page, ils polluent les chunks et créent du bruit sémantique
- **Tableaux multi-colonnes** : la lecture ligne par ligne mélange les colonnes (ex. : triangle de développement illisible)
- **Numéros de page et références croisées** : extraits comme du texte normal, ils parasitent les embeddings
- **Texte en filigrane ou en zones superposées** : peut être extrait dans un ordre inattendu
- **Formules mathématiques** : souvent mal rendues en texte brut (symboles remplacés par des caractères parasites)

> Stratégie : identifier et filtrer les zones problématiques via les coordonnées de bounding box (pdfplumber)

---

# Documents Word (.docx) — structure interne

- Le format .docx est une archive ZIP contenant des fichiers XML (document.xml, styles.xml, relations)
- La structure logique est riche : titres hiérarchisés (Heading 1/2/3), paragraphes, tableaux, listes numérotées
- Cette hiérarchie est précieuse pour le chunking : découper par section plutôt que par taille fixe
- Les documents Word contiennent souvent des métadonnées riches : auteur, date de création, version, organisation
- Les contenus dans les zones de texte flottantes ou les zones de commentaires peuvent être ignorés lors de l'extraction

---

# Documents Word — extraction

- **python-docx** : bibliothèque de référence pour lire et parcourir la structure d'un .docx (paragraphes, tableaux, styles)
- La hiérarchie des titres (styles Heading) permet de reconstruire le plan du document avant découpage
- Les tableaux Word sont accessibles ligne par ligne, cellule par cellule — utile pour les tableaux de provisions
- **docx2txt / mammoth** : alternatives plus simples pour l'extraction de texte brut sans structure
- Conserver les niveaux de titre comme métadonnées de chunk améliore significativement la pertinence du retrieval

> Exploiter la structure des styles Word pour un chunking sémantique plutôt que mécanique

---

# Fichiers Excel — types de données actuarielles

- **Tableaux de données** : sinistres payés, primes acquises, effectifs assurés — données tabulaires classiques
- **Triangles de développement** : matrices temporelles (années de survenance × années de développement)
- **Séries temporelles** : évolution mensuelle ou trimestrielle des indicateurs clés (S/P, fréquence, coût moyen)
- **Modèles de calcul** : cellules avec formules complexes (Chain-Ladder, Bornhuetter-Ferguson) — valeurs non lisibles directement
- **Tableaux de bord** : mélange de données, graphiques et commentaires — structure moins prévisible

---

# Fichiers Excel — extraction

- **openpyxl** : lecture native du format .xlsx, accès cellule par cellule, lecture des valeurs calculées (si sauvegardées)
- **pandas (read_excel)** : idéal pour charger des tableaux rectangulaires en DataFrame, gestion multi-onglets
- **xlrd** : compatibilité avec les anciens formats .xls (archives pré-2007)
- **calamine** : bibliothèque Rust-based très rapide, utile pour les très gros classeurs actuariels
- Toujours préciser l'onglet cible et les plages de cellules plutôt que de lire tout le classeur aveuglément

> Un classeur Excel peut contenir 10 onglets dont 9 non pertinents — la sélection manuelle reste souvent nécessaire

---

# Fichiers Excel — pièges spécifiques

- **Cellules fusionnées** : la valeur n'apparaît que dans la première cellule, les autres sont vides — trompe les parsers
- **Formules non calculées** : si le fichier n'a pas été ouvert/sauvegardé dans Excel, openpyxl lit la formule, pas le résultat
- **Lignes et colonnes cachées** : contiennent parfois des données intermédiaires importantes (hypothèses actuarielles)
- **Noms de plage** : les tableaux nommés facilitent la navigation mais ne sont pas toujours détectés automatiquement
- **Formats de date ambigus** : Excel stocke les dates comme entiers — la conversion peut introduire des décalages

---

# Gestion des métadonnées — pourquoi c'est crucial

- Dans un système RAG, retrouver **d'où vient** une information est aussi important que de la retrouver
- Les métadonnées permettent de filtrer les recherches (ex. : uniquement les documents de 2023, branche MRH)
- Elles facilitent l'audit : un actuaire doit pouvoir remonter à la source exacte d'un chiffre cité
- Sans métadonnées, deux chunks identiques provenant de versions différentes d'un rapport sont indiscernables
- Les exigences réglementaires (Solvabilité II, IFRS 17) imposent une traçabilité documentaire formelle

---

# Métadonnées utiles par document

| Métadonnée | Description | Exemples actuariels |
|---|---|---|
| `source` | Nom ou chemin du fichier d'origine | rapport_cloture_Q3_2024.pdf |
| `date` | Date de création ou de référence | 2024-09-30 |
| `auteur` | Rédacteur ou service producteur | Direction Actuariat MRH |
| `type` | Catégorie de document | rapport, triangle, note technique |
| `version` | Numéro de version ou statut | v2.1 — validé CCAR |
| `branche` | Ligne métier concernée | MRH, Auto, Santé, RC |
| `page` | Numéro de page du chunk extrait | 14 |

---

# Traçabilité des sources — exigences réglementaires

- **Solvabilité II** (directive 2009/138/CE) : exige que les calculs de provisions techniques soient documentés et reproductibles
- Le principe "Own Risk and Solvency Assessment" (ORSA) impose une traçabilité complète des hypothèses et données sources
- **IFRS 17** : chaque hypothèse actuarielle doit être justifiée et rattachée à des données observables documentées
- Les auditeurs internes et externes doivent pouvoir reconstituer tout calcul à partir des données sources
- Un système RAG sans traçabilité est inutilisable dans un contexte réglementaire actuariel

> Règle d'or : tout chunk récupéré doit embarquer les métadonnées permettant de retrouver le document source, la page et la version

---

# Pipeline d'ingestion — architecture générale

```
┌─────────────────────────────────────────────────────────┐
│                  DOCUMENTS SOURCES                      │
│      PDF  │  DOCX  │  XLSX  │  Images scannées          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    EXTRACTION                           │
│  pdfplumber / pymupdf │ python-docx │ openpyxl │ OCR    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   NETTOYAGE                             │
│  Suppression en-têtes │ Normalisation │ Déduplication   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  MÉTADONNÉES                            │
│  source │ date │ auteur │ type │ branche │ page         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   STOCKAGE                              │
│        Base vectorielle + store de métadonnées          │
└─────────────────────────────────────────────────────────┘
```

---

# Normalisation du texte extrait

- **Suppression des artefacts d'extraction** : caractères de contrôle, espaces multiples, retours à la ligne parasites
- **Uniformisation des encodages** : conversion systématique en UTF-8, gestion des caractères accentués
- **Nettoyage des en-têtes/pieds de page** : détection par récurrence (texte identique sur N pages consécutives)
- **Normalisation des nombres** : espaces de milliers, virgule/point décimal — critique pour les données actuarielles
- **Harmonisation des dates** : convertir tous les formats rencontrés vers un format ISO 8601 (YYYY-MM-DD)

> Un texte mal normalisé produit des embeddings bruités et dégrade la qualité du retrieval de façon invisible

---

# Gestion des erreurs d'extraction

- **Journaliser chaque fichier traité** : succès, avertissement ou échec, avec le message d'erreur complet
- **Ne jamais ignorer silencieusement une erreur** : un PDF non extrait est une source manquante dans le RAG
- **Classifier les erreurs** : fichier corrompu, format non supporté, OCR insuffisant, texte vide extrait
- **Mettre en quarantaine les documents problématiques** pour traitement manuel ultérieur
- **Tableaux de bord de pipeline** : taux de succès d'extraction, volume traité, erreurs par type de document

---

# Stockage intermédiaire des documents extraits

- Stocker le texte brut extrait avant chunking permet de re-traiter sans re-extraire (coûteux pour OCR)
- Format recommandé : JSON par document avec champs `texte`, `metadonnees`, `statut_extraction`, `date_traitement`
- Un store intermédiaire facilite l'audit : on peut inspecter ce qui a été fourni au pipeline de chunking
- La versioning des extractions permet de détecter les dérives si un fournisseur de document change de format
- Pour les très gros corpus : envisager un stockage objet (S3, Azure Blob) avec indexation des métadonnées

---

# Évaluation de la qualité d'extraction

- **Taux de caractères illisibles** : ratio de caractères non-ASCII inattendus ou de séquences incompréhensibles
- **Longueur moyenne des extractions** : un document de 50 pages qui produit 200 mots est suspect
- **Cohérence structurelle** : vérifier que les titres de sections sont bien présents dans le texte extrait
- **Échantillonnage manuel** : sur 5-10 % du corpus, comparer le texte extrait au document source visuellement
- **Métriques de couverture** : nombre de pages extraites vs nombre de pages total par document

---

# Bonnes pratiques d'ingestion

- Traiter chaque format avec la bibliothèque la plus adaptée — ne pas utiliser un outil généraliste pour tout
- Enrichir chaque document extrait avec ses métadonnées dès l'extraction, pas en post-traitement
- Versionner le pipeline d'ingestion : un changement de bibliothèque peut modifier les textes extraits
- Tester le pipeline sur un corpus réduit représentatif avant de traiter les milliers de documents
- Documenter les décisions de filtrage (pourquoi tel onglet Excel est ignoré, pourquoi tel en-tête est supprimé)

> Un pipeline d'ingestion robuste est la fondation invisible de tout système RAG de qualité

---

# Ce qu'on retient — Ingestion multi-format

- Chaque format (PDF, Word, Excel) requiert une stratégie d'extraction dédiée et des pièges spécifiques
- Les PDF scannés nécessitent une étape OCR avec validation de qualité avant toute utilisation
- Les métadonnées ne sont pas optionnelles : elles conditionnent la traçabilité et la conformité réglementaire
- Solvabilité II et IFRS 17 imposent que chaque donnée utilisée soit sourcée et reproductible
- Un pipeline d'ingestion robuste doit journaliser, gérer les erreurs et permettre la ré-extraction

---

# Stratégies de chunking

- Qu'est-ce que le chunking et pourquoi est-il critique ?
- Chunking par taille fixe, par paragraphe, par section
- Chunking sémantique et adaptatif
- L'overlap et son impact
- Évaluation et comparatif des stratégies

---

# Qu'est-ce que le chunking ?

- Le chunking consiste à découper un document en fragments (chunks) plus petits avant indexation
- Chaque chunk est encodé séparément par le modèle d'embedding et stocké dans le vecteur store
- Au moment de la requête, ce sont les chunks — pas les documents entiers — qui sont récupérés
- La frontière d'un chunk détermine quelles informations seront co-présentes lors de la génération
- Le chunking est une décision de design : elle conditionne la granularité de la connaissance exposée au LLM

---

# Pourquoi le chunking est-il critique ?

- Un chunk trop petit peut être hors contexte : une valeur de provision sans son libellé ne signifie rien
- Un chunk trop grand noie le signal pertinent dans du bruit et dépasse les limites du contexte du LLM
- La stratégie de chunking impacte directement le score de similarité lors du retrieval
- Un mauvais chunking peut faire échouer le RAG même avec un LLM de haute qualité
- Dans les documents actuariels, les tableaux et formules forment des unités sémantiques indissociables

---

# Chunking par taille fixe — principe

- Découpage séquentiel du texte en blocs de N tokens, sans tenir compte du contenu
- Simple à implémenter : aucune analyse linguistique ou structurelle requise
- Utilisé comme baseline pour comparer d'autres stratégies de chunking
- Peut découper une phrase, un tableau ou une formule actuarielle en plein milieu
- Adapté aux corpus homogènes où le texte est continu et sans structure forte

---

# Chunking par taille fixe — paramètres

- **chunk_size** : taille cible en tokens (ex : 256, 512, 1024) — à calibrer selon le type de document
- **overlap** : nombre de tokens répétés entre deux chunks consécutifs pour préserver le contexte aux frontières
- Paramètres typiques pour documents actuariels : taille = 512 tokens, overlap = 50 tokens
- Un overlap de 10-15 % de la taille du chunk est un point de départ raisonnable
- Ces deux paramètres doivent être tracés et versionnés : ils font partie du pipeline RAG

> L'overlap évite de perdre le contexte aux frontières des chunks

---

# Chunking par paragraphe — principe

- Chaque paragraphe du document devient un chunk, en s'appuyant sur les sauts de ligne doubles ou les balises
- Préserve l'unité thématique naturelle du texte : un paragraphe traite généralement d'une seule idée
- Nécessite une extraction de texte propre : les PDF mal structurés donnent des paragraphes fragmentés
- Dans les notes techniques, un paragraphe peut décrire une hypothèse actuarielle complète
- Moins de paramètres à régler que le chunking par taille fixe

---

# Chunking par paragraphe — avantages et limites

- **Avantages** : cohérence sémantique, respect de la structure éditoriale, peu de paramètres
- **Avantages** : chaque chunk récupéré est une unité de sens autonome et lisible par un expert métier
- **Limite** : longueur très variable — un paragraphe de 20 mots et un autre de 400 mots coexistent
- **Limite** : les documents PDF scannés ou mal convertis n'ont pas de séparateurs de paragraphes fiables
- **Limite** : les tableaux de sinistres ou de provisions ne se découpent pas naturellement en paragraphes

---

# Chunking par section (titres) — principe

- Regrouper le contenu sous un titre de section en un seul chunk : tout ce qui suit "§3.2 Provisions IARD" forme un bloc
- Exploite la structure hiérarchique des documents (niveaux de titres H1, H2, H3)
- Chaque chunk contient un contexte thématique cohérent défini par son intitulé de section
- Nécessite que le document soit bien structuré avec des titres explicites et parsables
- Les rapports de provisions Solvabilité II ont typiquement une structure normalisée exploitable

---

# Chunking par section — adapté aux rapports structurés

- Les rapports actuariels respectent souvent une structure standard : sommaire exécutif, hypothèses, résultats, annexes
- Chaque section (ex : "3. Triangle de développement des sinistres") est une unité sémantique forte
- Un chunk par section garantit que la méthode de calcul reste avec ses paramètres et ses résultats
- Risque : une section très longue (annexe avec 10 pages de tableaux) crée un chunk trop volumineux
- Solution : combiner avec une limite de taille maximale pour fragmenter les sections trop longues

> Pour un rapport de provisions de 80 pages, le chunking par section produit typiquement 15 à 30 chunks cohérents

---

# Chunking sémantique — principe

- Découper le texte aux endroits où le thème change, détecté par une mesure de similarité entre phrases
- Encoder chaque phrase et calculer la similarité avec la phrase suivante — une chute signale une rupture
- Produit des chunks dont les frontières coïncident avec des changements réels de sujet
- Plus coûteux en calcul que les stratégies basées sur la structure (titres, paragraphes)
- Nécessite un modèle d'embedding performant pour que la détection des ruptures soit fiable

---

# Chunking sémantique — détection des ruptures thématiques

- Calculer la similarité cosinus entre chaque paire de phrases consécutives dans une fenêtre glissante
- Définir un seuil de rupture : si la similarité tombe sous 0.75 (valeur indicative), on coupe
- Dans un rapport IFRS 17, le passage de "hypothèses de mortalité" à "courbes de taux" est une rupture naturelle
- Les tableaux de données créent souvent une rupture artificielle — les traiter séparément avant le chunking
- Le seuil est un hyperparamètre à calibrer sur un sous-ensemble annoté manuellement du corpus

---

# Chunking adaptatif — combiner les stratégies

- Aucune stratégie unique ne convient à tous les types de contenu dans un corpus hétérogène
- L'approche adaptative consiste à détecter le type de contenu et appliquer la stratégie correspondante
- Texte narratif → chunking par paragraphe ou sémantique
- Tableau de données → chunk = tableau entier ou ligne selon la taille
- Section structurée → chunking par titre avec limite de taille maximale
- Le pipeline doit classifier chaque bloc de contenu avant de choisir la méthode de découpage

---

# Chunking adaptatif selon le type de document

- **Rapport de provisions** : chunking par section H2/H3, limite à 800 tokens, overlap 80 tokens
- **Note technique** : chunking par paragraphe avec détection des blocs de formules à préserver entiers
- **Tableau de sinistres Excel** : chaque feuille ou groupe de lignes homogènes forme un chunk avec ses en-têtes
- **Correspondance e-mail** : chunking par message, avec ajout de métadonnées expéditeur/date/objet
- **Contrat d'assurance** : chunking par article avec numéro d'article inclus dans le texte du chunk

> La règle d'or : préserver les unités de sens métier, pas seulement les unités de longueur

---

# L'overlap — rôle et paramétrage

- L'overlap répète les K derniers tokens du chunk N au début du chunk N+1
- Rôle : éviter de perdre une information qui se trouve exactement à la frontière entre deux chunks
- Sans overlap, la phrase "le taux de sinistralité est donc de" peut être coupée avant "12,3 %"
- Overlap trop faible (< 5 %) : risque de perte aux frontières
- Overlap trop fort (> 30 %) : duplication excessive, bruit dans le retrieval et coût d'indexation augmenté
- Valeur recommandée : 10 à 20 % de la taille du chunk, soit 50-100 tokens pour un chunk de 512 tokens

---

# Impact du chunking sur le retrieval

- La qualité du retrieval dépend directement de la correspondance sémantique entre la requête et le chunk
- Un chunk qui coupe un tableau de sinistres en deux retourne une ligne sans en-tête : le LLM ne peut pas l'interpréter
- Exemple : requête "provision pour sinistres tardifs branche automobile 2023" — si la méthode et les chiffres sont dans deux chunks différents, le retrieval ne peut en récupérer qu'un
- Un chunk trop petit (50 tokens) aura un vecteur peu discriminant : similaire à de nombreux autres chunks
- Un chunk bien délimité autour d'une section "3.4 Best Estimate IARD" répond précisément à une requête ciblée

---

# Impact du chunking sur la précision des réponses

- Le LLM ne génère que ce qu'il reçoit dans son contexte : un chunk incomplet produit une réponse incomplète
- Si le chunk contient "le Best Estimate s'élève à" sans la valeur numérique (coupée au chunk suivant), la réponse sera vague
- Chunk trop large : le LLM peut se perdre dans du contenu non pertinent et halluciner des valeurs adjacentes
- Chunk idéal pour une question actuarielle : section + hypothèses + résultat numérique dans un même bloc
- Mesure concrète : tester avec des questions types et calculer le taux de réponses correctement chiffrées

> Un chunking mal calibré est souvent la première cause d'hallucinations dans un RAG documentaire

---

# Trop petits vs trop grands — le compromis

```
CHUNKS TROP PETITS                    CHUNKS TROP GRANDS
────────────────────                  ──────────────────────
[Provisions auto]  [= 12,3 M€]       [Section entière 3.1 à 3.8 = 2000 tokens]
│                  │                  │
│ Vecteur peu      │ Contexte         │ Noie le signal dans du bruit
│ discriminant     │ perdu            │ Dépasse parfois la fenêtre du LLM
│                  │                  │
└─ Retrieval       └─ LLM             └─ Réponses génériques,
   bruité            incomplet           peu précises

ZONE OPTIMALE : 256 – 800 tokens selon le type de contenu
```

- En dessous de 100 tokens : les embeddings manquent de contexte pour être précis
- Au-dessus de 1000 tokens : le ratio signal/bruit se dégrade, le retrieval devient moins ciblé
- La zone optimale dépend du modèle d'embedding, de la longueur des requêtes et du type de document

---

# Évaluation de la stratégie de chunking

- Constituer un jeu de questions-réponses de référence sur le corpus (20-50 paires QR annotées manuellement)
- Mesurer le **recall@k** : dans les k chunks récupérés, combien contiennent la bonne information ?
- Mesurer la **précision** : les chunks récupérés sont-ils pertinents ou introduisent-ils du bruit ?
- Comparer visuellement les chunks produits par chaque stratégie sur 5-10 documents représentatifs
- Itérer : modifier chunk_size ou la stratégie, re-indexer, re-évaluer — le processus est cyclique

> L'évaluation du chunking ne peut pas être entièrement automatisée : un expert métier doit valider la cohérence des chunks

---

# Comparatif des stratégies de chunking

| Stratégie | Avantages | Inconvénients | Idéal pour |
|---|---|---|---|
| Taille fixe | Simple, rapide | Coupe les idées | Corpus homogène |
| Par paragraphe | Respecte la structure | Tailles très variables | Articles, notes |
| Par section | Cohérence thématique | Dépend du balisage | Rapports structurés |
| Sémantique | Frontières naturelles | Coût de calcul | Textes complexes |
| Adaptatif | Flexible | Complexité d'implémentation | Corpus hétérogène |

---

# Bonnes pratiques de chunking

- Toujours inclure les en-têtes de tableau dans le chunk qui contient les données du tableau
- Ajouter le titre de section en préfixe de chaque chunk pour améliorer la qualité des embeddings
- Ne jamais séparer une formule actuarielle de ses paramètres d'application
- Tester au minimum deux stratégies différentes et mesurer objectivement avant de choisir
- Documenter la stratégie retenue et ses paramètres dans le registre du pipeline — un changement doit être traçable

---

# Ce qu'on retient — Chunking

- Le chunking est souvent la variable la plus impactante sur la qualité du RAG
- Pas de stratégie universelle : adapter au type de document et au cas d'usage
- Toujours tester plusieurs stratégies sur un échantillon représentatif
- L'overlap est quasi-indispensable pour les chunks de taille fixe

---
