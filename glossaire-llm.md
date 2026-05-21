# Glossaire — LLMs et systèmes RAG

Vocabulaire de référence pour la formation *Conception d'un système RAG pour l'exploitation de données actuarielles*.

---

## Architecture des modèles

**Attention**
Mécanisme qui pondère l'importance de chaque token par rapport aux autres. C'est le cœur du Transformer : plutôt que de lire séquentiellement, le modèle "regarde" tous les tokens simultanément et décide lesquels sont pertinents.

**Causal LM**
Modèle décodeur seul (GPT, Mistral, LLaMA) qui génère token par token en ne voyant que le passé. Opposé au MLM (voir ci-dessous).

**Context window**
Nombre maximum de tokens que le modèle peut traiter en une seule fois. Au-delà, le modèle "oublie" ce qui précède. Varie de 4 096 tokens (anciens modèles) à plus d'un million (Gemini 1.5).

**Cross-attention**
Mécanisme d'attention entre deux séquences différentes — typiquement de l'encodeur vers le décodeur dans les architectures encoder-decoder (T5, BART).

**Encoder / Decoder**
Deux familles d'architectures Transformer :
- Encoder seul (BERT) → compréhension, classification, embeddings
- Decoder seul (GPT, Mistral, LLaMA) → génération de texte
- Encoder-Decoder (T5, BART) → traduction, résumé

**Flash Attention**
Implémentation optimisée du mécanisme d'attention qui réduit drastiquement la consommation mémoire GPU. Transparent pour l'utilisateur, activé automatiquement dans les frameworks modernes.

**GQA / MQA (Grouped / Multi-Query Attention)**
Variantes de l'attention qui réduisent la taille du KV cache en partageant certaines clés/valeurs entre plusieurs têtes. Améliore la vitesse d'inférence.

**KV cache (Key-Value cache)**
Mécanisme qui mémorise les calculs d'attention déjà effectués pour ne pas les recalculer à chaque token généré. Essentiel pour des inférences rapides sur les longues séquences.

**MLM (Masked Language Modeling)**
Tâche d'entraînement de BERT : certains tokens sont masqués et le modèle doit les prédire. Donne un modèle bidirectionnel, excellent pour la compréhension mais pas pour la génération.

**MoE (Mixture of Experts)**
Architecture où le réseau est divisé en "experts" spécialisés et où seule une partie est activée pour chaque token. Permet d'augmenter la capacité du modèle sans augmenter proportionnellement le coût de calcul (ex : Mixtral 8×7B).

**Multi-head attention**
Plusieurs mécanismes d'attention fonctionnant en parallèle, chacun capturant un aspect différent des relations entre tokens. Leurs sorties sont concaténées.

**RoPE / ALiBi**
Méthodes d'encodage positionnel : façon dont le modèle "sait" à quelle position se trouve chaque token dans la séquence. RoPE (LLaMA, Mistral) et ALiBi favorisent une meilleure extrapolation aux longues séquences.

**Self-attention**
Attention d'un token sur tous les autres tokens de la même séquence. Permet de capturer les dépendances à longue distance ("il" dans "le président a dit qu'il viendrait").

**Transformer**
Architecture neuronale introduite par Vaswani et al. (2017) dans "Attention Is All You Need". Base de tous les LLMs modernes. Repose sur le mécanisme d'attention plutôt que sur les récurrences (RNN/LSTM).

---

## Tokenisation

**BPE (Byte Pair Encoding)**
Algorithme de tokenisation qui fusionne itérativement les paires de caractères/tokens les plus fréquentes. Utilisé par GPT, Mistral.

**SentencePiece**
Bibliothèque de tokenisation indépendante de la langue, capable de traiter du texte sans pré-segmentation. Utilisé par LLaMA, Mistral, T5.

**Token**
Unité de base traitée par le modèle. Approximativement ¾ de mot en anglais, souvent moins en français (les accents et caractères spéciaux créent des tokens supplémentaires). "actuariel" peut être découpé en 2-3 tokens selon le modèle.

**Tokenizer**
Système qui transforme le texte brut en séquence de tokens (entiers). Chaque modèle a son propre tokenizer — incompatible avec celui d'un autre modèle.

**Vocabulaire**
Ensemble de tous les tokens connus du modèle. Taille typique : 32 000 à 128 000 tokens.

**WordPiece**
Variante de BPE utilisée par BERT et ses dérivés.

---

## Entraînement

**BF16 / FP16**
Formats de représentation des nombres en 16 bits (demi-précision). Utilisés en entraînement pour réduire la mémoire GPU par deux par rapport au FP32, avec peu de perte de précision.

**Chinchilla**
Étude de DeepMind (2022) ayant montré que la plupart des LLMs sont sous-entraînés en données : pour un modèle de taille N, il faut environ 20×N tokens d'entraînement pour optimiser les performances.

**Data parallelism / Model parallelism / Tensor parallelism**
Stratégies pour distribuer l'entraînement sur plusieurs GPUs :
- Data : chaque GPU voit un batch différent
- Model : les couches sont réparties entre GPUs
- Tensor : les matrices d'une même couche sont réparties

**FLOPs**
Floating Point Operations — mesure standard du coût de calcul d'un modèle, en entraînement comme en inférence.

**FSDP (Fully Sharded Data Parallel)**
Technique PyTorch qui fragmente les poids, gradients et états de l'optimiseur entre tous les GPUs. Permet d'entraîner des modèles qui ne tiendraient pas sur un seul GPU.

**Gradient checkpointing**
Technique qui recompute les activations intermédiaires lors du backward plutôt que de les stocker. Réduit la mémoire GPU au prix d'un temps de calcul légèrement supérieur.

**Next token prediction**
Tâche principale d'entraînement des LLMs décodeurs : prédire le prochain token à partir de tous les précédents. Simple en apparence, extraordinairement puissante à grande échelle.

**Pre-training**
Phase d'entraînement initial sur un corpus massif (centaines de milliards à milliers de milliards de tokens). Très coûteuse, réalisée une seule fois par les équipes de recherche.

**Scaling laws**
Relations mathématiques (Kaplan et al., 2020) liant la taille du modèle, le volume de données et le budget de calcul à la performance. Ont guidé la course aux grands modèles.

**Self-supervised learning**
Apprentissage sans labels humains — la tâche de supervision est construite automatiquement à partir des données (prédire le token suivant, prédire le token masqué).

**ZeRO (Zero Redundancy Optimizer)**
Famille d'optimisations de DeepSpeed qui éliminent la redondance dans le stockage des états de l'optimiseur sur les systèmes distribués.

---

## Fine-tuning et adaptation

**Adapter layers**
Petites couches neuronales ajoutées entre les couches existantes du modèle. Seules ces couches sont entraînées, les poids originaux restent figés.

**Catastrophic forgetting**
Phénomène où le modèle "oublie" ses connaissances générales lors d'un fine-tuning trop agressif sur un domaine spécialisé.

**Constitutional AI**
Méthode développée par Anthropic pour aligner un modèle via un ensemble de principes (la "constitution") plutôt que par des annotations humaines massives.

**DPO (Direct Preference Optimization)**
Alternative plus simple à RLHF pour aligner un modèle sur des préférences humaines. Entraîne directement sur des paires de réponses (préférée / non préférée) sans modèle de récompense séparé.

**Fine-tuning**
Ré-entraînement d'un modèle pré-entraîné sur un corpus spécialisé ou des exemples spécifiques. Moins coûteux que le pré-entraînement mais modifie les poids du modèle.

**Instruction tuning**
Fine-tuning sur un ensemble d'instructions et de réponses attendues pour rendre le modèle capable de suivre des consignes en langage naturel.

**LoRA (Low-Rank Adaptation)**
Technique PEFT qui n'entraîne que deux petites matrices de rang faible par couche, au lieu de modifier tous les poids. Réduit le nombre de paramètres entraînables à ~1 % du total.

**PEFT (Parameter-Efficient Fine-Tuning)**
Famille de techniques (LoRA, Adapters, Prompt tuning…) permettant de fine-tuner un LLM en modifiant un très petit nombre de paramètres.

**PPO (Proximal Policy Optimization)**
Algorithme d'apprentissage par renforcement utilisé dans la phase RLHF. Optimise la politique du modèle (ses réponses) en fonction du score du reward model.

**Prefix tuning / Prompt tuning**
Techniques qui apprennent des tokens virtuels en entrée du modèle sans modifier les poids. Plus léger que LoRA, mais généralement moins performant.

**QLoRA**
Combine la quantisation INT4 et LoRA : permet de fine-tuner un modèle de 70B sur un seul GPU grand public en gardant des performances proches du fine-tuning complet.

**Reward model**
Modèle entraîné à scorer la qualité d'une réponse LLM selon les préférences humaines. Utilisé dans la boucle RLHF pour guider l'optimisation.

**RLHF (Reinforcement Learning from Human Feedback)**
Pipeline d'alignement en trois étapes : SFT → entraînement d'un reward model → optimisation par RL (PPO). Utilisé par GPT-4, Claude, Gemini.

**SFT (Supervised Fine-Tuning)**
Première étape du pipeline RLHF : entraînement supervisé sur des exemples de conversations de haute qualité annotés par des humains.

---

## Quantisation et compression

**AWQ (Activation-aware Weight Quantization)**
Méthode de quantisation qui identifie les poids les plus importants pour les activations et les préserve avec plus de précision.

**bitsandbytes**
Bibliothèque Python qui permet la quantisation INT8/INT4 à la volée lors du chargement d'un modèle HuggingFace.

**Distillation (Knowledge Distillation)**
Entraîner un petit modèle (student) à reproduire le comportement d'un grand modèle (teacher). Le student apprend non seulement les bonnes réponses mais aussi la distribution de probabilités du teacher.

**GGUF**
Format de fichier standard pour les modèles quantifiés, utilisé par llama.cpp et Ollama. Un seul fichier contient les poids quantifiés et les métadonnées du modèle.

**GPTQ**
Méthode de quantisation post-entraînement très répandue. Quantifie les poids couche par couche en minimisant l'erreur de reconstruction.

**INT8 / INT4 / INT2**
Niveaux de quantisation : les poids sont représentés sur 8, 4 ou 2 bits au lieu de 16 ou 32. Réduit la taille du modèle par 2× à 16× avec une perte de qualité variable.

**Pruning**
Suppression des poids proches de zéro ou d'importance faible pour alléger le modèle. Peut être non structuré (poids individuels) ou structuré (têtes d'attention entières).

**Quantisation**
Réduction de la précision numérique des poids pour diminuer la taille mémoire et accélérer l'inférence. Un modèle de 7B en FP16 ≈ 14 Go ; en INT4 ≈ 4 Go.

**Speculative decoding**
Technique d'inférence où un petit modèle "draft" propose plusieurs tokens, et le grand modèle les valide ou les rejette en parallèle. Accélère la génération sans changer la sortie finale.

---

## Inférence et génération

**Beam search**
Stratégie de décodage qui maintient les k meilleures hypothèses partielles à chaque étape. Plus précis que le greedy mais plus lent et parfois trop "lisse".

**Continuous batching**
Technique serveur qui regroupe dynamiquement des requêtes en cours de traitement plutôt que d'attendre la fin de chaque requête. Améliore significativement le débit.

**Greedy decoding**
Stratégie qui choisit toujours le token le plus probable. Déterministe, rapide, mais produit parfois des textes répétitifs ou plats.

**PagedAttention**
Gestion du KV cache par pages mémoire (comme un OS gère la RAM virtuelle). Permet à vLLM de servir beaucoup plus de requêtes simultanées.

**Repetition penalty**
Paramètre qui pénalise les tokens déjà générés pour éviter les boucles de répétition.

**Streaming**
Envoi des tokens au client au fur et à mesure de leur génération, plutôt qu'attendre la réponse complète.

**Temperature**
Paramètre qui contrôle le caractère aléatoire de la génération. 0 = déterministe (greedy), 1 = distribution naturelle, >1 = plus aléatoire et créatif.

**Throughput**
Nombre de tokens générés par seconde. Mesure clé de performance d'un serveur d'inférence.

**Top-k sampling**
Tire aléatoirement parmi les k tokens les plus probables. Évite les tokens très improbables sans être aussi restrictif que le greedy.

**Top-p (nucleus) sampling**
Tire parmi les tokens dont la probabilité cumulée dépasse p (ex : 0.9). Adaptatif : retient plus ou moins de tokens selon la certitude du modèle.

**TTFT (Time To First Token)**
Latence entre l'envoi du prompt et la réception du premier token de réponse. Mesure l'expérience utilisateur perçue.

---

## Prompting

**Chain-of-Thought (CoT)**
Technique qui demande au modèle de raisonner étape par étape ("think step by step") avant de donner sa réponse finale. Améliore significativement les performances sur les tâches de raisonnement.

**Few-shot**
Le prompt contient 2 à 5 exemples de la tâche attendue. Permet au modèle de "comprendre le format" sans fine-tuning.

**Function calling / Tool use**
Capacité d'un LLM à déclencher des fonctions externes (API, base de données, calculatrice) et à intégrer leurs résultats dans sa réponse.

**Grounding**
Ancrer la réponse du modèle dans des sources factuelles vérifiables plutôt que dans ses connaissances paramétriques. Principe central du RAG.

**Prompt injection**
Attaque consistant à injecter des instructions malveillantes dans le contexte fourni au modèle (documents, pages web, résultats de recherche) pour détourner son comportement.

**ReAct (Reasoning + Acting)**
Paradigme de prompting pour les agents LLM : alternance de phases de raisonnement (Thought) et d'actions (Act) avec observation des résultats.

**Self-consistency**
Générer plusieurs réponses avec des températures différentes et prendre la réponse majoritaire. Améliore la fiabilité sur les tâches de raisonnement.

**Structured output**
Forcer le modèle à répondre dans un format structuré (JSON, XML, Markdown). Essentiel pour l'intégration dans des pipelines applicatifs.

**System prompt**
Instructions données au modèle en amont de la conversation pour définir son rôle, ses contraintes et son comportement. Invisible pour l'utilisateur final.

**Tree of Thought (ToT)**
Extension du CoT : exploration arborescente de plusieurs raisonnements possibles avec évaluation et élagage des branches non prometteuses.

**Zero-shot**
Le modèle répond directement sans aucun exemple dans le prompt. Mesure la capacité de généralisation naturelle du modèle.

---

## RAG et retrieval

**Bi-encoder**
Architecture où la requête et les documents sont encodés séparément par le même modèle. Rapide (pré-calcul possible) mais moins précis qu'un cross-encoder.

**BM25**
Algorithme de recherche plein texte probabiliste (amélioration de TF-IDF). Très efficace et toujours compétitif pour la recherche par mots-clés exacts.

**Chunking**
Découpage des documents en fragments avant indexation. La taille et la stratégie de chunking impactent directement la qualité du retrieval.

**Cross-encoder**
Architecture de re-ranking qui traite la paire (requête, document) conjointement pour scorer leur pertinence. Plus précis qu'un bi-encoder mais trop lent pour la recherche initiale.

**Dense retrieval**
Recherche par similarité de vecteurs denses (embeddings). Capture la similarité sémantique, pas seulement lexicale.

**Embedding**
Représentation dense d'un texte sous forme de vecteur numérique. Des textes sémantiquement proches ont des vecteurs proches dans l'espace vectoriel.

**HNSW (Hierarchical Navigable Small World)**
Structure d'index pour la recherche approximative du plus proche voisin. Très rapide (O(log N)) au prix d'une légère imprécision.

**Hybrid search**
Combinaison de la recherche dense (embeddings) et sparse (BM25) pour bénéficier des avantages des deux approches.

**IVF (Inverted File Index)**
Structure d'index qui regroupe les vecteurs en clusters. La recherche interroge uniquement les clusters les plus proches de la requête.

**Lost in the middle**
Phénomène observé empiriquement : les LLMs utilisent mieux les informations placées en début et en fin de contexte qu'au milieu. À prendre en compte dans la construction du prompt RAG.

**MMR (Maximal Marginal Relevance)**
Algorithme de sélection des chunks qui équilibre pertinence et diversité pour éviter de fournir des informations redondantes au LLM.

**RAG (Retrieval-Augmented Generation)**
Architecture qui augmente un LLM avec une base de connaissances externe : les documents pertinents sont retrouvés puis injectés dans le prompt avant la génération.

**Re-ranking**
Étape post-retrieval qui re-score les k premiers résultats avec un modèle plus précis (cross-encoder) pour améliorer leur ordre avant injection dans le prompt.

**Sparse retrieval**
Recherche basée sur des vecteurs creux (TF-IDF, BM25) où seuls les mots présents ont une valeur non nulle.

**Top-k retrieval**
Récupération des k documents/chunks les plus similaires à la requête. La valeur de k est un hyperparamètre clé du pipeline RAG.

---

## Évaluation

**Answer Relevance**
Métrique RAG mesurant si la réponse générée répond effectivement à la question posée.

**Context Recall**
Métrique RAG mesurant si les chunks pertinents ont bien été retrouvés lors du retrieval.

**ELO (Chatbot Arena)**
Système de classement des LLMs par comparaison directe par des humains (LMSYS Chatbot Arena). Reflète la préférence utilisateur réelle.

**Faithfulness**
Métrique RAG mesurant si la réponse est fidèle au contexte fourni — le modèle ne doit pas introduire d'informations absentes des chunks.

**GSM8K**
Benchmark de 8 500 problèmes mathématiques niveau collège. Mesure le raisonnement arithmétique.

**Hallucination**
Le modèle génère des informations factuellement incorrectes mais présentées avec assurance. Principal risque des LLMs en contexte professionnel.

**HumanEval**
Benchmark de 164 problèmes de programmation Python. Mesure la capacité de génération de code.

**LLM-as-judge**
Utilisation d'un LLM puissant (GPT-4, Claude) pour évaluer automatiquement les réponses d'un autre LLM. Moins coûteux que l'évaluation humaine.

**MMLU (Massive Multitask Language Understanding)**
Benchmark couvrant 57 domaines académiques (mathématiques, droit, médecine, histoire…). Standard de facto pour mesurer les connaissances générales.

**MT-Bench**
Benchmark d'évaluation multi-tour (conversation) par un LLM juge. Mesure la capacité à maintenir une conversation cohérente.

**Perplexité**
Mesure à quel point un modèle est "surpris" par un texte de test. Inverse de la probabilité moyenne assignée aux tokens. Plus basse = meilleur modèle.

**RAGAS**
Framework open source d'évaluation des systèmes RAG. Mesure faithfulness, answer relevance et context recall de façon automatique.

**ROUGE**
Famille de métriques pour évaluer les résumés automatiques par comparaison avec des résumés de référence.

---

## Modèles et formats

**Checkpoint**
Sauvegarde des poids d'un modèle à un instant précis de l'entraînement. Permet de reprendre un entraînement interrompu ou de comparer différentes étapes.

**Foundation model**
Grand modèle pré-entraîné sur un corpus massif, conçu pour être adapté à de nombreuses tâches. GPT-4, LLaMA, Mistral sont des foundation models.

**GGUF**
Format de fichier binaire pour les modèles quantifiés. Standard de facto pour l'inférence locale (Ollama, llama.cpp). Un seul fichier autonome.

**HuggingFace Hub**
Plateforme centrale hébergeant des milliers de modèles, datasets et espaces de démonstration open source.

**Model card**
Documentation standardisée d'un modèle : cas d'usage, limitations, données d'entraînement, performances sur les benchmarks, considérations éthiques.

**Open weights**
Modèles dont les poids sont publiés (LLaMA, Mistral, Gemma). Différent de l'open source au sens strict : les données et le code d'entraînement ne sont pas toujours publiés.

**Safetensors**
Format de sérialisation des poids développé par HuggingFace. Conçu pour être sûr (pas d'exécution de code arbitraire au chargement) et rapide.

---

## Sécurité et alignement

**Alignment**
Ensemble de techniques visant à faire en sorte qu'un LLM se comporte de façon utile, honnête et inoffensive (helpful, harmless, honest — les "3H" d'Anthropic).

**Bias**
Les LLMs reproduisent et parfois amplifient les biais présents dans leurs données d'entraînement (biais de genre, culturels, politiques…).

**Constitutional AI**
Méthode Anthropic : le modèle s'auto-évalue et se corrige selon un ensemble de principes éthiques explicites, réduisant la dépendance aux annotations humaines.

**Guardrails**
Couche de filtrage en amont et/ou en aval du LLM pour détecter et bloquer les contenus indésirables (toxicité, données personnelles, hors sujet).

**Jailbreak**
Technique visant à contourner les garde-fous d'un LLM par des prompts spécialement construits pour lui faire ignorer ses instructions de sécurité.

**Prompt injection**
Attaque où des instructions malveillantes sont dissimulées dans des données externes (documents, pages web) traitées par le LLM pour détourner son comportement.

**Red teaming**
Processus de test adversarial : une équipe cherche activement à faire produire au modèle des sorties indésirables, pour identifier et corriger ses failles avant déploiement.

**Watermarking**
Technique statistique qui marque le texte généré par un LLM de façon imperceptible pour l'humain mais détectable par un algorithme. Permet de distinguer texte humain et texte généré.

---

## Déploiement et infrastructure

**API gateway**
Point d'entrée unique qui gère l'authentification, le rate limiting et le routage vers les différents modèles d'un serveur d'inférence.

**Inference server**
Serveur spécialisé pour servir des LLMs en production : Ollama (usage local), vLLM (haute performance), TGI (HuggingFace), llama.cpp (CPU/GPU mixte).

**On-premise**
Déploiement sur l'infrastructure propre de l'organisation, sans dépendance cloud. Répond aux contraintes de confidentialité des données (RGPD, données sensibles).

**OpenAI-compatible API**
Standard d'API adopté par la plupart des serveurs d'inférence alternatifs. Permet de remplacer l'API OpenAI par un modèle local sans changer le code client.

**Rate limiting**
Limite du nombre de requêtes par unité de temps pour protéger l'infrastructure et gérer les coûts.

**Serverless inference**
Inférence hébergée dans le cloud sans gestion de serveur — on paie par token généré (ex : API OpenAI, Anthropic, Mistral AI).

---

*Document généré dans le cadre de la formation RAG Groupama — Mai 2026*
