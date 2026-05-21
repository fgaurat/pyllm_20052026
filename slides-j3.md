---
marp: true
theme: your-theme
paginate: true
title: "RAG pour données actuarielles — Jour 3"
header: "Conception d'un système RAG — Jour 3"
footer: "© Claude et Frédéric Gaurat 2026"
---

# Conception d'un système RAG
## pour l'exploitation de données actuarielles

### Jour 3 — Production documentaire & Chatbot local

**Durée** : 7h  |  **Prérequis** : Jours 1 et 2 complétés  |  **Public** : Développeurs / Data analysts

---

# Programme — Jour 3

## Matin
- Génération de rapports Word automatisés (python-docx)
- Génération de présentations PowerPoint (python-pptx)

## Après-midi
- Chatbot local avec Ollama
- Intégration chatbot + RAG

---

<!-- _class: lead -->
# Jour 3 — Matin
## Production documentaire automatisée

---

<!-- _class: lead -->
# Génération de rapports Word avec python-docx

---

# Cas d'usage : rapports actuariels automatisés

- **Notes techniques** de provisions (Best Estimate, Risk Margin) générées à la demande
- **Rapports de sinistralité** mensuels ou trimestriels alimentés par les données du SI
- **Reporting IFRS 17** : tableaux de réconciliation, narrative automatique
- **Mémoires Solvabilité II** : ORSA, RSR, SFCR avec sections textuelles générées par LLM
- **Rapports de clôture** : consolidation de données, commentaires de gestion

> L'enjeu : produire un document Word conforme à la charte, sans intervention manuelle sur la mise en forme

---

# python-docx — présentation de la bibliothèque

- **python-docx** est une bibliothèque Python open source pour créer et modifier des fichiers `.docx`
- Compatible avec les formats Microsoft Word 2007 et supérieurs
- Permet de manipuler tous les éléments d'un document : paragraphes, tableaux, styles, images, en-têtes, pieds de page
- Installable via pip, sans dépendance à Microsoft Word
- Largement utilisée dans les pipelines de génération documentaire automatisée
- Intégration naturelle avec les sorties de LLM (texte brut → document structuré)

| Capacité | Disponible |
|---|---|
| Créer un document from scratch | Oui |
| Ouvrir et modifier un template | Oui |
| Appliquer des styles Word | Oui |
| Insérer tableaux et images | Oui |

---

# Structure d'un document Word

Un document Word se décompose en objets hiérarchiques :

- **Document** — objet racine, point d'entrée unique ; contient tous les éléments du fichier `.docx`
- **Paragraph** — unité de texte de base ; porte le style de paragraphe (Normal, Heading 1, etc.) et les propriétés d'espacement
- **Run** — fragment de texte à l'intérieur d'un paragraphe ; porte la mise en forme de caractères (gras, italique, police, taille)
- **Table** — grille de cellules ; chaque cellule contient elle-même des paragraphes et des runs

```
Document
 └── Paragraph (style: Heading 1)
      └── Run ("Titre du rapport")
 └── Paragraph (style: Normal)
      └── Run ("Texte courant ")
      └── Run ("en gras", bold=True)
 └── Table
      └── Row → Cell → Paragraph → Run
```

> Un même paragraphe peut contenir plusieurs runs avec des mises en forme différentes

---

# Créer un document Word from scratch — concept

**Principe général :**

1. Instancier un objet `Document` vide
2. Ajouter des éléments dans l'ordre d'apparition souhaité (titres, paragraphes, tableaux)
3. Appliquer les styles et la mise en forme à chaque élément
4. Sauvegarder le fichier `.docx`

**Ce qu'on peut construire ainsi :**
- Titres hiérarchiques (Heading 1, Heading 2, Heading 3)
- Paragraphes de texte courant
- Listes à puces ou numérotées
- Tableaux de données
- Séparateurs de page

**Limites de l'approche from scratch :**
- La charte graphique doit être reconstituée manuellement
- Les logos, couleurs et polices maison ne sont pas présents par défaut
- Chronophage et fragile à maintenir

---

# Styles et mise en forme — principe

**Deux niveaux de mise en forme dans Word :**

- **Styles de paragraphe** — définissent l'apparence globale d'un bloc : `Normal`, `Heading 1`, `Body Text`, `Caption`…
- **Styles de caractère** — s'appliquent à un run : `Strong`, `Emphasis`, `Intense Quote`…

**Propriétés directes (overrides) :**
- Taille, famille et couleur de police
- Gras, italique, souligné
- Alignement, retrait, espacement avant/après
- Couleur de fond de cellule (tableaux)

**Bonne pratique :**
- Privilégier les **styles nommés** plutôt que les propriétés directes
- Les styles nommés se propagent depuis le template → cohérence garantie
- Les propriétés directes créent une mise en forme "dure" difficile à maintenir

> En contexte actuariel, les styles sont définis dans le template de l'entreprise — ne pas les recréer manuellement

---

# Travailler avec les styles existants d'un template

**Étapes pour exploiter les styles d'un document existant :**

1. Ouvrir le fichier template `.docx` (rapport N-1 ou modèle officiel)
2. Lister les styles disponibles dans le document
3. Identifier le nom exact des styles maison (`Titre Rapport`, `Corps Actuariel`, `Tableau Données`…)
4. Appliquer ces styles par leur nom lors de la génération

**Précautions :**
- Les noms de styles peuvent différer selon la langue de Word (FR vs EN)
- Un style absent du template provoque un fallback sur `Normal`
- Vérifier la correspondance nom style ↔ rendu visuel avant la mise en production

**Styles actuariels typiques à identifier :**
- Style de titre de section (numérotation automatique)
- Style de tableau de provisions
- Style de note de bas de page réglementaire
- Style de légende de graphique

---

# Approche par template — principe

- Partir d'un document Word existant (rapport N-1 ou modèle officiel)
- Identifier les **zones variables** à remplacer (chiffres, textes générés)
- Conserver la mise en forme, les styles, les logos de la charte
- Remplacer le contenu programmatiquement avec python-docx

> Ne jamais partir de zéro : les templates existants portent la charte graphique de l'entreprise

---

# Approche par template — avantages pour la charte graphique

**Ce que le template apporte automatiquement :**

- Logo Groupama en en-tête, pied de page avec numérotation conforme
- Polices, couleurs et espacements validés par la Direction Communication
- Styles de titres hiérarchiques déjà configurés
- Tableaux pré-formatés aux couleurs de la marque
- Mise en page (marges, orientation) conforme aux standards internes

**Impact opérationnel :**

| Sans template | Avec template |
|---|---|
| Mise en forme à reconstruire | Charte héritée automatiquement |
| Risque de non-conformité | Document conforme dès le premier run |
| Maintenance lourde | Un seul fichier template à maintenir |
| Validation manuelle | Validation réduite au contenu |

> Le template est un actif à gérer : le versionner, le tester, le mettre à jour lors des changements de charte

---

# Injecter du texte généré par le LLM

**Flux d'injection :**

```
RAG retrieval → Contexte pertinent
      ↓
LLM prompt → Texte narratif généré
      ↓
Post-traitement → Découpage en paragraphes
      ↓
python-docx → Insertion dans le document Word
```

**Points d'attention :**
- Le LLM retourne du texte brut : découper sur les sauts de ligne pour créer des paragraphes distincts
- Appliquer le style approprié à chaque paragraphe (corps de texte, note, avertissement)
- Nettoyer les artefacts de génération : espaces multiples, tirets incorrects, guillemets non typographiques
- Tronquer si la longueur dépasse la zone prévue dans le template

**Cas actuariel typique :**
- Commentaire de sinistralité : généré par LLM à partir des données du trimestre
- Analyse des écarts de provisions : narrative structurée en 3 paragraphes (observation, cause, impact)

---

# Injecter des données chiffrées (tables, KPIs actuariels)

**Principe de séparation des responsabilités :**

- Les **données chiffrées** viennent toujours du SI ou des modèles actuariels — jamais du LLM
- Le **LLM commente** les données ; il ne les génère pas
- python-docx insère les chiffres directement depuis les DataFrames ou dictionnaires Python

**KPIs actuariels typiques à injecter :**

| KPI | Source |
|---|---|
| Best Estimate Provisions | Modèle actuariel |
| Loss Ratio (S/P) | Base de données sinistres |
| Combined Ratio | Calcul interne |
| SCR, MCR (Solvabilité II) | Modèle interne / formule standard |
| Contractual Service Margin (IFRS 17) | Système comptable |

**Règle de validation :**
- Toujours comparer le chiffre injecté avec la source avant export
- Journaliser les valeurs injectées pour auditabilité

---

# Créer et remplir des tableaux Word

**Structure d'un tableau python-docx :**

```
Table
 ├── Row 0 (en-tête)
 │    ├── Cell(0,0) : "Garantie"
 │    ├── Cell(0,1) : "Provisions N"
 │    └── Cell(0,2) : "Provisions N-1"
 └── Row 1 (données)
      ├── Cell(1,0) : "RC Auto"
      ├── Cell(1,1) : "125 M€"
      └── Cell(1,2) : "118 M€"
```

**Étapes de construction :**
1. Définir le nombre de lignes et de colonnes à la création
2. Remplir les cellules ligne par ligne
3. Appliquer le style de tableau du template (`Table Grid`, `Tableau Actuariel`…)
4. Mettre en gras la ligne d'en-tête
5. Aligner les colonnes numériques à droite

**Piège courant :** python-docx ne gère pas nativement la fusion de cellules complexe — préférer un tableau simple quand c'est possible

---

# Ajouter des en-têtes et pieds de page

**Structure dans python-docx :**
- Chaque section du document possède son propre en-tête et pied de page
- Première page différente possible (couverture sans en-tête)
- Pages paires/impaires différentes pour les documents recto-verso

**Contenu typique pour un rapport actuariel :**

*En-tête :*
- Logo Groupama (image)
- Titre du rapport
- Référence du document / version

*Pied de page :*
- Numéro de page / nombre de pages total
- Mention de confidentialité (`CONFIDENTIEL — Usage interne`)
- Date de génération automatique

**Approche recommandée :**
- Utiliser le template : les en-têtes et pieds de page sont déjà configurés
- Modifier uniquement les éléments variables (titre, date, version)
- Ne pas reconstruire l'en-tête from scratch — risque de perte du logo

---

# Gestion de la pagination

**Contrôle des sauts de page :**
- **Saut de page explicite** : insérer un paragraphe avec la propriété `page_break_before`
- **Saut de section** : changer l'orientation ou les marges à mi-document
- **Éviter les coupures** : propriété `keep_together` pour empêcher qu'un tableau soit coupé entre deux pages

**Cas d'usage actuariels :**

| Situation | Traitement |
|---|---|
| Chaque garantie sur une nouvelle page | Saut de page avant chaque section |
| Tableau de provisions trop long | Répétition des en-têtes de tableau |
| Page de garde séparée | Section distincte sans en-tête/pied |
| Annexes paginées séparément | Numérotation redémarrée en section |

**Bonne pratique :**
- Tester la pagination sur le contenu le plus long prévisible
- Les tableaux générés dynamiquement peuvent déborder — prévoir une logique de découpage

---

# Insérer des images et graphiques

**Types d'images supportés :**
- PNG, JPEG, BMP, GIF (images statiques)
- Graphiques exportés depuis matplotlib, plotly, seaborn au format PNG/SVG

**Pipeline d'insertion d'un graphique actuariel :**

```
Données actuarielles (DataFrame)
      ↓
Génération du graphique (matplotlib)
      ↓
Export PNG en mémoire (BytesIO)
      ↓
python-docx : add_picture(stream, width)
      ↓
Paragraphe de légende avec style "Caption"
```

**Points d'attention :**
- Définir la largeur en centimètres pour contrôler la mise en page (ex : 15 cm pour une pleine largeur)
- Toujours ajouter une légende sous l'image (numérotation automatique si le style le permet)
- Les graphiques interactifs (plotly HTML) ne sont pas insérables — exporter en PNG d'abord
- Résolution recommandée : 150-300 dpi pour un rendu imprimable correct

---

# Génération conditionnelle de sections

**Principe :**
Certaines sections du rapport n'existent que si les données le justifient — ne pas générer de sections vides.

**Exemples actuariels de conditions :**

| Condition | Section générée |
|---|---|
| Sinistres graves présents (> seuil) | Section "Analyse des grands risques" |
| Écart de provisions > 5% | Section "Explication des écarts significatifs" |
| Nouveau périmètre IFRS 17 | Annexe de réconciliation comptable |
| Ratio S/P dégradé vs N-1 | Commentaire d'alerte en encadré |
| Données manquantes détectées | Avertissement méthodologique |

**Implémentation logique :**
- Évaluer chaque condition avant la génération
- Passer un dictionnaire de flags booléens au générateur de document
- Chaque section est une fonction indépendante, appelée ou non selon le flag
- Journaliser les sections générées et omises pour traçabilité

> La génération conditionnelle réduit le bruit dans les rapports et améliore la lisibilité pour les réviseurs

---

# Pipeline complet : RAG → LLM → Word

```
┌─────────────────────────────────────────────────────────┐
│                     DONNÉES EN ENTRÉE                   │
│  Base vectorielle  │  SI actuariel  │  Template .docx   │
└────────┬───────────┴───────┬────────┴────────┬──────────┘
         │                   │                 │
         ▼                   ▼                 ▼
┌─────────────────┐  ┌───────────────┐  ┌─────────────────┐
│  RAG Retrieval  │  │  Extraction   │  │  Ouverture du   │
│  (top-k chunks) │  │  KPIs / Data  │  │  template Word  │
└────────┬────────┘  └───────┬───────┘  └────────┬────────┘
         │                   │                   │
         └──────────┬────────┘                   │
                    ▼                            │
         ┌──────────────────┐                   │
         │   LLM Prompt     │                   │
         │  (narratif +     │                   │
         │   commentaires)  │                   │
         └────────┬─────────┘                   │
                  │                             │
                  └──────────────┬──────────────┘
                                 ▼
                    ┌────────────────────────┐
                    │   Générateur python-   │
                    │   docx                 │
                    │  - Titres & sections   │
                    │  - Tableaux de données │
                    │  - Texte narratif LLM  │
                    │  - Graphiques PNG      │
                    │  - En-têtes / pieds    │
                    └────────────┬───────────┘
                                 ▼
                    ┌────────────────────────┐
                    │   Validation +         │
                    │   Export .docx final   │
                    └────────────────────────┘
```

---

# Gestion des erreurs de génération

**Catégories d'erreurs à anticiper :**

- **Données manquantes** : un KPI absent du SI → valeur de substitution (`N/D`) ou section omise
- **Texte LLM invalide** : réponse vide, trop longue, ou contenant des artefacts
- **Style introuvable** : nom de style mal orthographié → fallback sur `Normal` avec alerte
- **Image corrompue** : fichier PNG manquant ou illisible → placeholder ou saut
- **Template inaccessible** : fichier verrouillé ou absent → arrêt avec message explicite

**Stratégie de gestion :**

| Type d'erreur | Comportement recommandé |
|---|---|
| Donnée manquante | Valeur de substitution + flag dans le journal |
| Erreur LLM | Retry × 2, puis texte de fallback prédéfini |
| Erreur fatale (template) | Arrêt immédiat + notification |
| Avertissement non bloquant | Continuer + ajouter note dans le rapport |

> Toujours produire un document partiel plutôt que rien — le réviseur peut compléter manuellement

---

# Validation du document généré

**Niveaux de validation à implémenter :**

1. **Validation structurelle**
   - Le fichier `.docx` est bien formé (non corrompu)
   - Tous les signets / zones variables ont été remplacés
   - Aucune balise de template résiduelle (`{{PROVISION_BE}}` non substituée)

2. **Validation du contenu**
   - Les chiffres clés correspondent aux données sources (contrôle de cohérence)
   - Le nombre de pages est dans la plage attendue (ex : 15–25 pages)
   - Les sections obligatoires sont présentes

3. **Validation métier**
   - Les totaux des tableaux sont corrects (somme des lignes = total)
   - Les ratios calculés sont dans des bornes raisonnables
   - La date de génération est correcte

**Outillage :**
- python-docx peut relire le document généré pour vérifier la structure
- Comparer les valeurs injectées avec un dictionnaire de référence
- Générer un rapport de validation JSON aux côtés du `.docx`

---

# Bonnes pratiques de génération documentaire

**Organisation du code :**
- Séparer la **logique de génération** (structure du document) de la **logique métier** (calculs, appels LLM)
- Une fonction par section du rapport → maintenabilité et testabilité
- Centraliser les constantes : noms de styles, largeurs de colonnes, seuils de validation

**Gestion des templates :**
- Versionner le template `.docx` dans le dépôt Git (avec le code)
- Nommer les templates avec la version : `rapport_provisions_v2.3.docx`
- Ne jamais modifier le template en production — passer par une revue

**Traçabilité et audit :**
- Journaliser chaque génération : timestamp, données source, version du template, version du modèle LLM
- Stocker les documents générés avec leur contexte de génération (métadonnées)
- Conserver les données brutes utilisées pour permettre la reproductibilité

**Sécurité des données :**
- Ne jamais inclure de données personnelles dans les logs de génération
- Chiffrer les documents contenant des données confidentielles avant transmission
- Appliquer les règles de rétention documentaire (PSSI, politique archivage)

---

# Ce qu'on retient — Génération Word

**Les fondamentaux :**
- python-docx permet de créer et modifier des `.docx` sans Microsoft Word
- La hiérarchie Document → Paragraph → Run → Table structure tout document
- L'approche par template est **toujours préférable** à la construction from scratch

**Le pipeline RAG → LLM → Word :**
- RAG fournit le contexte pertinent pour le LLM
- Le LLM génère la narrative ; les données chiffrées viennent du SI
- python-docx assemble le tout dans le template de la charte graphique

**En contexte actuariel :**
- Les provisions, ratios et KPIs sont injectés directement — jamais générés par le LLM
- La génération conditionnelle évite les sections vides ou non pertinentes
- La validation du document généré est indispensable avant diffusion

**À retenir pour la suite :**
- Même logique pour python-pptx (présentations PowerPoint)
- Le générateur de document est un composant du pipeline RAG, pas une fin en soi
- Documenter le mapping template ↔ données pour chaque rapport automatisé

---

<!-- _class: lead -->
# Génération de présentations PowerPoint avec python-pptx

---

# Cas d'usage : présentations automatisées pour comités

**Comités de direction et instances de gouvernance :**
- **Comité de pilotage sinistres** : tableau de bord mensuel (fréquence, coût moyen, S/P)
- **Comité Solvabilité II** : mise à jour trimestrielle des ratios de couverture SCR/MCR
- **CODIR actuariel** : suivi des provisions techniques, évolution Best Estimate
- **Reporting IFRS 17** : présentation des agrégats de portefeuille aux commissaires

**Ce que l'automatisation apporte :**
- Mise à jour en quelques secondes au lieu de plusieurs heures de mise en forme
- Cohérence garantie entre les données SI et les slides présentées
- Libération du temps expert pour l'analyse, pas la mise en page
- Traçabilité : chaque slide est générée depuis une source de données identifiée

> Un actuaire qui automatise ses slides passe sa réunion à commenter, pas à corriger des chiffres

---

# python-pptx — présentation de la bibliothèque

**Qu'est-ce que python-pptx ?**
- Bibliothèque Python pure pour créer et modifier des fichiers `.pptx` (format OpenXML)
- Aucun logiciel Microsoft Office requis sur le serveur de production
- Lecture, modification et création de présentations depuis zéro ou depuis un template

**Ce qu'elle sait faire :**
- Ouvrir un template et injecter du texte dans les placeholders
- Ajouter, supprimer, dupliquer des slides
- Créer et remplir des tableaux et des graphiques
- Insérer des images, modifier les couleurs et les polices
- Accéder à la structure complète d'un fichier PPTX (slides, layouts, masters)

**Ce qu'elle ne fait pas :**
- Rendre un PDF ou afficher une prévisualisation (il faut LibreOffice ou PowerPoint)
- Gérer les animations et transitions complexes (lecture seule sur ces éléments)
- Modifier des formes vectorielles complexes (SmartArt notamment)

**Installation :** `pip install python-pptx`

---

# Structure d'un fichier PPTX

**Hiérarchie des objets python-pptx :**

```
Presentation
├── Slide Master (charte graphique globale)
│   └── Slide Layout (modèles de mise en page)
│       └── Placeholder (zones nommées : titre, corps, image...)
└── Slide (diapositive concrète)
    └── Shape (tout élément visible)
        ├── TextFrame → Paragraph → Run (texte)
        ├── Table → Row → Cell
        ├── Chart (graphique)
        └── Picture (image)
```

**Les 4 objets clés à maîtriser :**

| Objet | Rôle | Accès python-pptx |
|---|---|---|
| `Presentation` | Conteneur du fichier | `prs = Presentation("template.pptx")` |
| `Slide` | Une diapositive | `prs.slides[0]` ou `prs.slides.add_slide(layout)` |
| `Shape` | Tout élément visible | `slide.shapes` |
| `TextFrame` | Conteneur de texte | `shape.text_frame` |

---

# Ouvrir et modifier un template PowerPoint existant

**Pourquoi travailler avec un template :**
- La charte graphique (couleurs, polices, logo) est déjà en place
- Les layouts sont calibrés par le service communication
- On ne refait pas ce qui existe : on injecte les données dans les zones prévues

**Flux de travail recommandé :**

1. Ouvrir le template `.pptx` avec `Presentation("template.pptx")`
2. Identifier les layouts disponibles (slide 6 de ce module)
3. Ajouter une slide depuis le bon layout : `prs.slides.add_slide(layout)`
4. Remplir les placeholders avec les données
5. Sauvegarder sous un nouveau nom : `prs.save("rapport_2026_T1.pptx")`

**Règle d'or :**
- Ne jamais écraser le template source — toujours sauvegarder dans un nouveau fichier
- Versionner le template dans Git avec les scripts qui l'utilisent
- Documenter les index de placeholder dans un fichier de configuration

---

# Les layouts — comprendre et utiliser les placeholders

**Un layout = un modèle de diapositive avec des zones prédéfinies**

Chaque layout porte un nom (ex. : "Titre seul", "Titre et contenu", "Deux colonnes") et contient des **placeholders** numérotés.

**Types de placeholders courants :**

| idx | Type | Contenu typique |
|---|---|---|
| 0 | TITLE | Titre de la diapositive |
| 1 | BODY / OBJECT | Texte principal, tableau, graphique |
| 2 | SUBTITLE | Sous-titre (layouts de couverture) |
| 10+ | Personnalisés | Définis par le template d'entreprise |

**Inspecter les layouts d'un template :**
- Lister les layouts : `for layout in prs.slide_layouts: print(layout.name)`
- Lister les placeholders d'un layout : `for ph in layout.placeholders: print(ph.placeholder_format.idx, ph.name)`

> Toujours inspecter le template avant de coder — les idx varient selon les chartes graphiques

---

# Modifier le texte dans les placeholders

**Accès à un placeholder par son index :**
- `slide.placeholders[0]` → titre
- `slide.placeholders[1]` → corps de texte

**Structure du texte : TextFrame → Paragraph → Run**
- `text_frame.text = "valeur"` remplace tout le contenu (perd la mise en forme)
- Méthode recommandée : effacer les paragraphes existants, puis ajouter les nouveaux

**Bonnes pratiques :**
- Effacer avec `tf.clear()` avant d'écrire pour éviter les résidus
- Ajouter paragraphe par paragraphe avec `tf.add_paragraph()`
- Contrôler le niveau de retrait (bullet level) avec `paragraph.level = 1`
- Hériter de la mise en forme du template en ne surchargeant que ce qui change

**Cas actuariel — remplissage d'une slide KPI :**
- Titre : "Sinistralité T1 2026 — Branche Auto"
- Corps : liste de KPIs (fréquence, coût moyen, S/P, résultat technique)
- Valeurs injectées depuis le SI, libellés depuis le template de configuration

---

# Ajouter et modifier des tableaux

**Créer un tableau dans une slide :**
- Utiliser `slide.shapes.add_table(rows, cols, left, top, width, height)`
- Retourne un objet `GraphicFrame` ; accéder au tableau via `.table`
- Remplir cellule par cellule : `table.cell(row_idx, col_idx).text = valeur`

**Structure recommandée pour les tableaux actuariels :**

| Ligne | Colonne 1 | Colonne 2 | Colonne 3 |
|---|---|---|---|
| En-tête | Indicateur | Valeur T4 2025 | Valeur T1 2026 |
| Données | Fréquence sinistre | 4,2 % | 4,5 % |
| Données | Coût moyen | 3 210 € | 3 350 € |
| Données | Ratio S/P | 68,1 % | 71,3 % |

**Mise en forme des tableaux :**
- Couleur de fond d'une cellule : modifier le XML via `cell._tc` (niveau bas)
- Largeur des colonnes : `table.columns[i].width = Cm(4)`
- Hauteur des lignes : `table.rows[i].height = Cm(1)`
- Police : `cell.text_frame.paragraphs[0].runs[0].font.bold = True`

---

# Insérer des graphiques depuis des données

**python-pptx supporte les graphiques natifs Office (via openpyxl en coulisses) :**

**Types de graphiques disponibles :**
- `XL_CHART_TYPE.BAR_CLUSTERED` — barres groupées (comparaisons de branches)
- `XL_CHART_TYPE.LINE` — courbes (évolution temporelle des provisions)
- `XL_CHART_TYPE.PIE` — camembert (répartition du portefeuille)
- `XL_CHART_TYPE.COLUMN_CLUSTERED` — colonnes groupées (KPIs trimestriels)

**Processus de création :**
1. Définir les données dans un objet `ChartData`
2. Ajouter les séries : `chart_data.add_series("S/P", (68.1, 71.3, 69.8, 72.0))`
3. Insérer dans la slide : `slide.shapes.add_chart(chart_type, left, top, width, height, chart_data)`

**Alternatives pour les graphiques complexes :**
- Générer le graphique avec matplotlib → exporter en PNG → insérer comme image
- Plus de contrôle visuel, moins de dépendance au rendu Office
- Recommandé pour les courbes de triangle de développement ou les heat maps

---

# Approche : slide modèle → duplication → remplissage

**Pourquoi dupliquer une slide modèle plutôt que créer from scratch :**
- La slide modèle contient exactement la mise en forme voulue (couleurs, tailles, positions)
- On duplique la structure, on remplace uniquement le contenu
- Aucun risque de décalage par rapport à la charte graphique

**Pattern recommandé :**

```
Template PPTX
└── Slide 1 : Couverture (à remplir)
└── Slide 2 : Slide KPI modèle (à dupliquer N fois)
└── Slide 3 : Slide tableau modèle (à dupliquer M fois)
└── Slide 4 : Conclusion (à remplir)
```

**Étapes de duplication :**
1. Copier l'élément XML de la slide modèle (`slide._element`)
2. Créer une nouvelle slide et y coller le XML copié
3. Mettre à jour les relations (images, graphiques liés)
4. Remplir les placeholders texte avec les nouvelles données

> Cette approche est plus robuste que `add_slide(layout)` quand le template est complexe

---

# Pipeline complet : données RAG → slides PowerPoint

1. **Retrieval** — Récupérer les données du corpus via le RAG
2. **Génération** — Demander au LLM de structurer les résultats en bullets
3. **Templating** — Ouvrir le template PowerPoint N-1
4. **Injection** — Remplir les placeholders avec les données générées
5. **Export** — Sauvegarder le nouveau fichier `.pptx`

> L'humain valide le contenu, l'automatisation gère le formatage

---

# Gestion des images et icônes

**Insérer une image dans une slide :**
- `slide.shapes.add_picture(image_path, left, top, width, height)`
- L'image est embarquée dans le fichier PPTX (pas de lien externe)
- Formats supportés : PNG, JPEG, GIF, BMP, TIFF, WMF, EMF

**Cas d'usage actuariels :**
- **Logo entité** : inséré depuis un chemin fixe dans le template de configuration
- **Graphique matplotlib** : exporté en PNG puis inséré (`savefig("kpi.png", dpi=150)`)
- **Cartographie des risques** : heat map générée par le pipeline et insérée
- **Signature numérique** ou tampon "CONFIDENTIEL" : image PNG positionnée en overlay

**Bonnes pratiques :**
- Stocker les assets (logos, icônes) dans un dossier `assets/` versionné
- Utiliser des PNG en haute résolution (150+ dpi) pour les présentations projetées
- Supprimer les images temporaires générées après insertion
- Ne jamais hardcoder des chemins absolus — utiliser `pathlib.Path` et des chemins relatifs au projet

---

# Contrôle de la mise en forme (couleurs, polices)

**Couleurs en python-pptx :**
- Couleur RVB : `font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)` (bleu corporate)
- Couleur de fond d'une forme : `shape.fill.solid()` puis `shape.fill.fore_color.rgb = RGBColor(...)`
- Récupérer la couleur d'un élément du template pour la réutiliser

**Polices :**
- Famille : `font.name = "Calibri"`
- Taille : `font.size = Pt(14)`
- Gras : `font.bold = True`
- Italique : `font.italic = True`

**Stratégie recommandée — héritage du template :**

| Approche | Avantage | Inconvénient |
|---|---|---|
| Surcharger tout | Contrôle total | Fragile si le template change |
| Héritage maximal | Robuste aux évolutions du template | Moins de contrôle |
| **Héritage + surcharge ciblée** | **Équilibre recommandé** | Nécessite de bien connaître le template |

> Règle : ne surcharger que ce qui doit impérativement être différent du template

---

# Génération de slides de KPIs actuariels

**Architecture d'une slide KPI type comité de direction :**

```
┌─────────────────────────────────────────────┐
│  TITRE : Sinistralité Auto — T1 2026        │
├──────────────┬──────────────┬───────────────┤
│  Fréquence   │  Coût moyen  │  Ratio S/P    │
│   4,5 %      │   3 350 €    │   71,3 %      │
│  ▲ +0,3 pt   │  ▲ +140 €   │  ▲ +3,2 pts   │
├──────────────┴──────────────┴───────────────┤
│  Commentaire : Hausse de la fréquence       │
│  concentrée sur le segment jeunes           │
│  conducteurs (18-25 ans, zone urbaine)      │
└─────────────────────────────────────────────┘
```

**Éléments injectés automatiquement :**
- Valeurs numériques : issues directement du SI (aucune intervention LLM)
- Variations vs période N-1 : calculées par le pipeline Python
- Commentaire : généré par le LLM à partir des données et du contexte RAG
- Période et branche : paramètres d'entrée du pipeline

---

# Limites de python-pptx

**Limites techniques :**
- Pas de rendu visuel natif — il faut PowerPoint ou LibreOffice pour voir le résultat
- Les animations, transitions et effets complexes ne sont pas modifiables
- SmartArt : lecture possible, modification très limitée
- Graphiques existants : la modification de données est possible mais délicate
- Les polices doivent être installées sur la machine cible (pas embarquées)

**Limites opérationnelles :**
- Un fichier PPTX corrompu par une mauvaise manipulation XML peut ne plus s'ouvrir
- La duplication de slides avec des graphiques liés nécessite de mettre à jour les relations
- Les templates très complexes (masters multiples, contenus groupés) peuvent produire des surprises

**Alternatives à considérer :**
- **LibreOffice UNO** : conversion PPTX → PDF en ligne de commande (pour l'export automatique)
- **Google Slides API** : si l'entreprise est sur G Suite
- **Aspose.Slides** : bibliothèque commerciale plus complète (formats exotiques, animations)
- **Approche hybride** : python-pptx pour l'injection + PowerPoint macros VBA pour le rendu final

---

# Stratégie de test : ouvrir le fichier et vérifier visuellement

**Pourquoi les tests automatisés ne suffisent pas pour le PPTX :**
- Un fichier valide XML peut produire un rendu visuellement incorrect
- Les décalages de mise en page ne sont détectables qu'à l'œil
- Les polices manquantes ou les couleurs non appliquées nécessitent une ouverture réelle

**Protocole de validation recommandé :**

| Étape | Action | Fréquence |
|---|---|---|
| 1. Test structurel | Vérifier que le fichier s'ouvre sans erreur | Chaque génération |
| 2. Test des données | Contrôler que les valeurs injectées sont correctes | Chaque génération |
| 3. Test visuel rapide | Ouvrir dans LibreOffice Impress ou PowerPoint | À chaque évolution du code |
| 4. Revue complète | Parcourir toutes les slides générées | Avant chaque diffusion |

**Tests automatisables avec python-pptx :**
- Vérifier le nombre de slides généré
- Contrôler que les placeholders clés ne sont pas vides
- Valider les valeurs numériques injectées par comparaison avec la source
- Tester que toutes les images référencées existent bien

---

# Intégration avec le pipeline RAG des jours 1 et 2

**Le pipeline complet jours 1-2-3 :**

```
[Corpus documentaire]
       │
       ▼
[Embeddings + Index vectoriel]  ← Jour 1
       │
       ▼
[RAG : Retrieval + LLM]         ← Jour 2
       │
       ├──► [python-docx → rapport Word]   ┐
       │                                    ├─ Jour 3
       └──► [python-pptx → slides PPTX]   ┘
```

**Points de connexion avec le RAG :**
- Le contexte récupéré par le RAG alimente le LLM pour les commentaires narratifs
- Les données chiffrées (KPIs, provisions) viennent du SI — pas du RAG ni du LLM
- Le pipeline RAG peut aussi récupérer des slides N-1 pour contextualiser la génération
- La même requête RAG peut alimenter simultanément le Word et le PPTX

**Paramétrage du pipeline pour les slides :**
- Définir un prompt système spécifique "tu génères du contenu pour des slides PowerPoint"
- Contraindre la longueur des bullets (max 8 mots par bullet pour la lisibilité en salle)
- Séparer clairement ce que le LLM génère (narrative) et ce qu'il ne touche pas (chiffres)

---

# Bonnes pratiques de génération PPTX

**Organisation du projet :**
- Stocker template, assets et scripts dans le même dépôt Git
- Versionner les templates avec un numéro de version dans le nom
- Séparer la logique de données (calculs, SI) de la logique de présentation (mise en page)

**Robustesse :**
- Toujours tester si un placeholder existe avant d'y écrire (`try/except` sur l'accès)
- Gérer les cas où une valeur est `None` ou manquante (afficher "N/D" plutôt que planter)
- Logger chaque slide générée avec ses données sources pour la traçabilité
- Sauvegarder dans un répertoire daté pour faciliter les comparaisons

**Qualité du rendu :**
- Limiter le texte : une slide = une idée, max 5-6 bullets de max 10 mots
- Privilégier les tableaux et graphiques aux listes de chiffres bruts
- Respecter scrupuleusement les placeholders du template (ne pas créer de nouvelles zones)
- Tester le rendu sur le projecteur de la salle de réunion avant le jour J

**Gouvernance des données :**
- Identifier clairement sur chaque slide la source et la date de la donnée
- Ne jamais laisser le LLM inventer des chiffres — validation systématique avant diffusion
- Appliquer les règles de confidentialité (classification des données, accès restreint)

---

# Ce qu'on retient — Génération PowerPoint

**Les fondamentaux :**
- python-pptx lit et écrit des fichiers `.pptx` sans Microsoft Office
- La hiérarchie Presentation → Slide → Shape → TextFrame structure tout
- L'approche template est indispensable : on injecte, on ne recrée pas

**Le pipeline RAG → LLM → PPTX :**
- RAG fournit le contexte documentaire et les données N-1
- Le LLM génère la narrative et les bullets ; les KPIs viennent du SI
- python-pptx assemble le tout dans la charte graphique de l'entreprise

**En contexte actuariel :**
- Les valeurs numériques (S/P, provisions, SCR) ne passent jamais par le LLM
- Chaque slide KPI doit afficher la source et la période de la donnée
- La validation visuelle avant diffusion est non négociable

**À retenir pour la suite :**
- Même logique pour les autres formats (Excel avec openpyxl, PDF avec reportlab)
- Le générateur PPTX est un composant du pipeline RAG, pas une application autonome
- Documenter le mapping placeholder ↔ données pour chaque template utilisé

---

<!-- _class: lead -->
# Jour 3 — Après-midi
## Chatbot local avec Ollama et mise en perspective production

---

# Chatbot local avec Ollama

**Objectifs de cette section :**
- Comprendre pourquoi déployer un LLM en local en entreprise
- Installer et configurer Ollama
- Choisir et tester des modèles adaptés aux contraintes matérielles
- Utiliser l'API Ollama dans un pipeline existant

**Plan :**
1. Motivations et enjeux de confidentialité
2. Présentation d'Ollama et de son architecture
3. Installation, premiers pas, modèles disponibles
4. API, paramètres, fenêtre de contexte
5. Limites, bonnes pratiques, monitoring

---

# Pourquoi un LLM local ?

**Contraintes fréquentes en entreprise :**
- Données sensibles ne pouvant pas quitter le SI (actuariat, RH, juridique)
- Connexion internet restreinte ou filtrée
- Politique de sécurité interdisant les API cloud externes
- Besoin de maîtriser la version du modèle utilisé (reproductibilité)

**Avantages d'un déploiement local :**
- Aucune donnée transmise à un tiers
- Latence réseau éliminée
- Coût marginal nul après acquisition du matériel
- Disponibilité offline (pas de dépendance à un fournisseur cloud)

> Un LLM local n'est pas une copie dégradée — c'est une architecture différente, adaptée à des contraintes différentes.

---

# Confidentialité et souveraineté — l'argument clé

**Cadre réglementaire :**
- **RGPD (art. 28)** : tout traitement de données personnelles par un sous-traitant requiert un DPA ; les API cloud sont des sous-traitants
- **Données actuarielles** : cotations individuelles, historiques sinistres, provisions — souvent classifiées "confidentiel" ou "secret des affaires"
- **Directive NIS2** : les opérateurs d'importance vitale (dont certains assureurs) renforcent l'exigence de maîtrise des outils

**Ce qu'un LLM cloud peut voir :**
- Le texte intégral de vos requêtes (donc les données incluses dans le prompt)
- Les documents injectés dans le contexte (RAG)
- Les réponses générées (logs chez le fournisseur)

**Ce qu'un LLM local voit :**
- Rien ne sort du périmètre du SI

> Règle simple : si la donnée ne peut pas être envoyée par e-mail à un prestataire, elle ne doit pas figurer dans un prompt cloud.

---

# Ollama — présentation

**Ollama** est un outil open-source qui permet de télécharger, gérer et exécuter des LLM en local sur macOS, Linux et Windows.

**Ce qu'Ollama fait :**
- Gère le téléchargement et le stockage des modèles (format GGUF)
- Lance un serveur HTTP local exposant une API REST
- Gère la quantization automatique selon la RAM disponible
- Compatible avec l'API d'OpenAI (drop-in replacement)

**Ce qu'Ollama ne fait pas :**
- Il n'entraîne pas les modèles
- Il ne gère pas le fine-tuning (c'est le rôle d'autres outils)

**Licence :** MIT — utilisation commerciale autorisée

**Dépôt :** `github.com/ollama/ollama` — +100 000 étoiles GitHub

---

# Ollama — architecture

```
┌─────────────────────────────────────────────────┐
│                   Poste utilisateur              │
│                                                  │
│  ┌───────────┐     HTTP      ┌────────────────┐  │
│  │  Client   │ ◄──────────► │  ollama serve  │  │
│  │ (curl /   │  :11434       │  (serveur REST)│  │
│  │  LangChain│               └───────┬────────┘  │
│  │  /OpenAI) │                       │            │
│  └───────────┘               ┌───────▼────────┐  │
│                               │  llama.cpp     │  │
│                               │  (moteur GGUF) │  │
│                               └───────┬────────┘  │
│                                       │            │
│                               ┌───────▼────────┐  │
│                               │  Modèle .gguf  │  │
│                               │  ~/.ollama/    │  │
│                               └────────────────┘  │
└─────────────────────────────────────────────────┘
```

- L'API REST écoute sur `http://localhost:11434`
- Endpoint `/api/chat` compatible avec `openai.ChatCompletion`
- Toutes les inférences restent sur le CPU/GPU local

---

# Installation d'Ollama

**macOS**

```
# Via le site officiel
curl -fsSL https://ollama.com/install.sh | sh

# Ou via Homebrew
brew install ollama
```

**Linux (Ubuntu / Debian)**

```
curl -fsSL https://ollama.com/install.sh | sh
# Le service systemd est configuré automatiquement
```

**Windows**

- Télécharger l'installateur `.exe` depuis `ollama.com`
- Fonctionne nativement sur Windows 10/11 (64 bits)
- Support GPU NVIDIA via CUDA, AMD via ROCm

**Vérification**

```
ollama --version
# ollama version 0.x.y

curl http://localhost:11434/api/tags
# {"models": [...]}
```

---

# Premiers pas — pull et run d'un modèle

**Télécharger un modèle**

```
ollama pull mistral
# Télécharge mistral:latest (~4 GB)

ollama pull llama3
# Télécharge llama3:latest (~4.7 GB)

ollama pull phi3:mini
# Modèle compact (~2.3 GB)
```

**Lancer une session interactive**

```
ollama run mistral
# >>> Bonjour, peux-tu résumer ce paragraphe ?
# ...réponse...
# >>> /bye
```

**Lister les modèles téléchargés**

```
ollama list
# NAME            ID              SIZE    MODIFIED
# mistral:latest  61e88e884507    4.1 GB  2 hours ago
# llama3:latest   365c0bd3c000    4.7 GB  1 hour ago
```

---

# Les modèles disponibles dans Ollama

**Catalogue officiel :** `ollama.com/library`

| Famille | Éditeur | Points forts |
|---|---|---|
| Llama 3 / 3.1 / 3.2 | Meta | Très bon français, open weights |
| Mistral / Mixtral | Mistral AI | Européen, license permissive |
| Phi-3 / Phi-4 | Microsoft | Ultra-compact, efficace |
| Gemma / Gemma 2 | Google | Légère, multilingue |
| Qwen 2.5 | Alibaba | Excellentes perfs en code |
| DeepSeek-R1 | DeepSeek | Raisonnement, chain-of-thought |
| Command-R | Cohere | Optimisé RAG |

**Format de tag :**

```
ollama pull llama3:8b          # 8 milliards de paramètres
ollama pull llama3:70b         # 70 milliards (serveur dédié)
ollama pull mistral:7b-q4_0   # Quantization 4 bits explicite
```

---

# Llama 3 — caractéristiques et usage

**Famille Llama 3 (Meta, 2024)**

- Versions : 8B, 70B, 405B (paramètres)
- Licence : Meta Llama 3 Community License — usage commercial autorisé < 700M MAU
- Très bon support du français (entraîné sur davantage de données multilingues que Llama 2)

**Points forts :**
- Compréhension de documents longs (contexte 8K tokens natif, extensible)
- Qualité de raisonnement proche des modèles cloud sur les tâches métier
- Bonne gestion des instructions système (system prompt)

**Usage recommandé chez Groupama :**
- Résumés de notes techniques et rapports
- Extraction d'entités (montants, dates, clauses) dans des documents juridiques
- Génération de commentaires de gestion à partir de données structurées

**Commande :**

```
ollama pull llama3:8b
ollama run llama3:8b
```

---

# Mistral 7B — bon équilibre performance / ressources

**Mistral 7B (Mistral AI, Paris)**

- 7 milliards de paramètres, architecture transformeur avec GQA et sliding window attention
- Licence Apache 2.0 — usage commercial libre, sans restriction
- Éditeur européen : engagement RGPD et souveraineté numérique

**Performances :**
- Surpasse Llama 2 13B sur la plupart des benchmarks
- Excellent rapport qualité / RAM requise
- Instruction-tuned via `mistral:instruct` — mieux pour les chatbots

**Variantes disponibles :**

| Tag | Taille | Usage |
|---|---|---|
| `mistral:7b` | ~4 GB | Base, à éviter en chat |
| `mistral:instruct` | ~4 GB | Chat et instructions |
| `mixtral:8x7b` | ~26 GB | Haute qualité, MoE |

> Mistral est le choix par défaut pour un déploiement professionnel sur un poste 16 GB.

---

# Phi-3 (Microsoft) — modèle compact

**Famille Phi-3 (Microsoft Research)**

- Phi-3 Mini : 3.8B paramètres — tourne sur 4 GB RAM
- Phi-3 Small : 7B paramètres
- Phi-3 Medium : 14B paramètres
- Phi-4 (2025) : 14B, performances nettement améliorées

**Philosophie :**
- Entraîné sur des données de haute qualité (livres scolaires, code synthétique)
- Performances étonnantes au regard de la taille
- Idéal pour les postes avec ressources limitées

**Limites :**
- Moins performant que Mistral 7B sur les tâches longues et la compréhension de documents
- Fenêtre de contexte plus courte (4K tokens sur Phi-3 Mini)
- Français moins fluide que Llama 3

**Quand choisir Phi-3 :**
- Tests rapides sur un poste avec 8 GB RAM
- Prototypage avant déploiement sur un modèle plus grand
- Tâches courtes et bien définies (extraction, classification)

---

# Gemma (Google) — alternative légère

**Famille Gemma (Google DeepMind)**

- Gemma 2B, 7B (Gemma 1, 2024)
- Gemma 2 : 2B, 9B, 27B (2024) — nettes améliorations
- Licence : Gemma Terms of Use (usage commercial autorisé, redistributable)

**Points forts :**
- Architecture moderne (basée sur Gemini)
- Très bonne qualité sur les tâches de compréhension
- Gemma 2 9B compétitif avec Mistral 7B

**Comparaison rapide :**

| Modèle | RAM | Français | Code | Raisonnement |
|---|---|---|---|---|
| Gemma 2B | 2 GB | ⭐⭐ | ⭐⭐ | ⭐ |
| Gemma 7B | 5 GB | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Gemma 2 9B | 6 GB | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

**Usage recommandé :**
- Alternative à Phi-3 sur des postes contraints
- Bonne option si déjà dans l'écosystème Google (Vertex AI + Gemma local en dev)

---

# Choisir un modèle selon les ressources disponibles

| Modèle | RAM requise | Qualité | Usage recommandé |
|---|---|---|---|
| Phi-3 mini | 4 GB | ⭐⭐ | Tests rapides, poste modeste |
| Mistral 7B | 8 GB | ⭐⭐⭐ | Bon équilibre, usage professionnel |
| Llama 3 8B | 8 GB | ⭐⭐⭐ | Très bon français |
| Mixtral 8x7B | 32 GB | ⭐⭐⭐⭐ | Haute qualité, serveur dédié |

> Pour la formation : Mistral 7B ou Llama 3 8B sur un poste avec 16 GB RAM

---

# L'API Ollama — compatible OpenAI

Ollama expose deux API REST en local :

**API native Ollama**

```
POST http://localhost:11434/api/chat
{
  "model": "mistral",
  "messages": [{"role": "user", "content": "Résume ce texte : ..."}]
}
```

**API compatible OpenAI** (endpoint `/v1/`)

```
POST http://localhost:11434/v1/chat/completions
{
  "model": "mistral",
  "messages": [{"role": "user", "content": "Résume ce texte : ..."}]
}
```

**Avantage clé :** en changeant l'URL de base et le nom du modèle dans votre configuration, tout code écrit pour l'API OpenAI fonctionne avec Ollama sans modification.

**Dans LangChain :**

```
# base_url pointe vers le serveur local
# model = nom du modèle ollama
# Aucun autre changement nécessaire
```

---

# Paramètres de génération

**Les trois paramètres essentiels :**

| Paramètre | Valeur par défaut | Effet |
|---|---|---|
| `temperature` | 0.8 | Créativité — 0.0 = déterministe, 1.0 = aléatoire |
| `top_p` | 0.9 | Nucleus sampling — limite le pool de tokens candidats |
| `num_ctx` | 2048 | Taille de la fenêtre de contexte en tokens |

**Recommandations selon les tâches :**

- **Extraction / classification** : `temperature=0.0`, `top_p=1.0`
- **Résumé** : `temperature=0.3`, `top_p=0.9`
- **Génération de texte métier** : `temperature=0.5`, `top_p=0.9`
- **Brainstorming** : `temperature=0.8`, `top_p=0.95`

**Attention :** `num_ctx` consomme de la VRAM/RAM — doubler le contexte multiplie la consommation mémoire par ~2.

> Pour les pipelines RAG, fixer `temperature=0.1` à `0.3` et `num_ctx` à la taille maximale supportée par le matériel.

---

# Fenêtre de contexte et modèles locaux

**Rappel — la fenêtre de contexte :**
- Nombre maximum de tokens que le modèle peut traiter en une seule inférence
- Inclut le system prompt, l'historique de conversation, les documents injectés ET la réponse

**Contextes natifs des modèles courants :**

| Modèle | Contexte natif | Extensible via Ollama |
|---|---|---|
| Phi-3 Mini | 4K tokens | Oui (dégradation possible) |
| Mistral 7B | 8K tokens | Jusqu'à 32K |
| Llama 3 8B | 8K tokens | Jusqu'à 128K |
| Mixtral 8x7B | 32K tokens | Non |

**Impact sur le RAG :**
- Un contexte 8K ≈ 5-6 pages A4 de texte — suffisant pour 3-4 chunks de 512 tokens
- Augmenter `num_ctx` dans Ollama dépasse le contexte natif mais dégrade la qualité
- Stratégie : calibrer la taille des chunks RAG selon le contexte disponible

> Règle pratique : réserver 25 % du contexte au system prompt et à la question, 75 % aux chunks RAG.

---

# Limites des LLM locaux vs cloud

| Dimension | LLM local (Ollama) | LLM cloud (OpenAI, Mistral API) |
|---|---|---|
| Confidentialité | Totale | Selon CGU et DPA |
| Qualité max | Modèles 70B+ avec GPU | GPT-4o, Claude Opus |
| Vitesse | Dépend du matériel | Très rapide (GPU datacenter) |
| Contexte max | 8K–128K selon modèle | 128K–1M tokens |
| Coût à l'usage | 0 (matériel existant) | Facturation à la requête |
| Mise à jour | Manuelle | Automatique |
| Fine-tuning | Possible (llama.cpp) | Via API (coûteux) |

**Cas où le cloud reste préférable :**
- Données non sensibles + besoin de la meilleure qualité possible
- Pics de charge imprévisibles (scalabilité élastique)
- Équipes sans compétences DevOps pour maintenir un serveur LLM

> La bonne question n'est pas "local ou cloud ?" mais "quelles données, quelle qualité requise, quel budget matériel ?"

---

# Stratégies pour contourner les limites

**Limite : qualité insuffisante du modèle local**

- Stratégie 1 — **Prompt engineering renforcé** : few-shot examples, chain-of-thought explicite
- Stratégie 2 — **Décomposition des tâches** : plusieurs appels séquentiels plutôt qu'un seul prompt complexe
- Stratégie 3 — **Router local/cloud** : données non sensibles → cloud, données sensibles → local

**Limite : fenêtre de contexte trop petite**

- Réduire la taille des chunks RAG (256 tokens au lieu de 512)
- Limiter le nombre de chunks injectés (top-3 au lieu de top-5)
- Implémenter un résumé intermédiaire des chunks les plus longs

**Limite : vitesse trop lente**

- Activer le GPU si disponible (`OLLAMA_GPU_LAYERS` ou variable d'environnement)
- Utiliser une quantization plus agressive (Q4 au lieu de Q8)
- Mettre en cache les réponses fréquentes (LRU cache applicatif)

> L'architecture hybride (local pour la confidentialité, cloud pour les tâches complexes non sensibles) est souvent la meilleure réponse opérationnelle.

---

# Monitoring et gestion des ressources

**Surveiller les ressources en temps réel :**

```
# CPU et RAM (Linux/macOS)
htop
# ou
top -pid $(pgrep ollama)

# GPU NVIDIA
nvidia-smi -l 1

# GPU AMD
rocm-smi --showuse
```

**Variables d'environnement Ollama utiles :**

| Variable | Effet |
|---|---|
| `OLLAMA_NUM_PARALLEL` | Nombre de requêtes simultanées (défaut : 1) |
| `OLLAMA_MAX_LOADED_MODELS` | Modèles gardés en mémoire (défaut : 1) |
| `OLLAMA_GPU_LAYERS` | Couches déléguées au GPU |
| `OLLAMA_KEEP_ALIVE` | Durée de mise en cache du modèle en RAM |

**Alertes à surveiller :**
- RAM swap actif → le modèle est trop grand pour la RAM disponible
- CPU > 95 % en continu → réduire `OLLAMA_NUM_PARALLEL`
- Latence first-token > 10 s → envisager un modèle plus petit ou quantization Q4

---

# Bonnes pratiques de déploiement local

**Isolation et sécurité :**
- Ollama écoute sur `localhost` par défaut — ne pas exposer le port 11434 sur le réseau sans authentification
- Si accès multi-utilisateurs nécessaire : mettre un reverse proxy Nginx avec authentification basic ou token
- Journaliser les requêtes (modèle appelé, timestamp, taille du prompt) pour l'audit

**Gestion des modèles :**
- Versionner les modèles utilisés en production (`ollama pull mistral:7b-instruct-v0.3`)
- Ne pas utiliser le tag `:latest` en production — il peut pointer vers une version différente après mise à jour
- Documenter les paramètres de génération utilisés pour chaque cas d'usage

**Intégration pipeline :**
- Tester le comportement du modèle sur un jeu de données de référence avant déploiement
- Prévoir un fallback si Ollama ne répond pas (timeout, circuit breaker)
- Documenter la configuration matérielle minimale requise dans le README du projet

**En contexte Groupama :**
- Valider avec la DSSI la liste des modèles autorisés avant déploiement
- Stocker les modèles sur un partage réseau sécurisé pour éviter les re-téléchargements
- Inclure Ollama dans le périmètre des revues de sécurité annuelles

---

# Ce qu'on retient — Ollama

**Les fondamentaux :**
- Ollama installe et expose un LLM local via une API REST compatible OpenAI
- Aucune donnée ne quitte le périmètre du SI — réponse directe aux enjeux RGPD et souveraineté
- Le format GGUF et la quantization permettent de faire tourner des modèles 7B sur un poste standard

**Choisir le bon modèle :**
- Mistral 7B Instruct = référence pour un usage professionnel sur 16 GB RAM
- Phi-3 Mini = solution de repli sur poste contraint (8 GB)
- Llama 3 8B = meilleure option si le français est prioritaire

**Dans un pipeline RAG :**
- Remplacer l'URL de base OpenAI par `http://localhost:11434/v1/` suffit dans LangChain
- Calibrer `num_ctx` selon la taille des chunks et le nombre de documents injectés
- Fixer `temperature` bas (0.1–0.3) pour des réponses factuelles et reproductibles

**À retenir pour la suite :**
- La session suivante intègre Ollama dans le pipeline RAG complet
- L'architecture hybride local/cloud est la réponse pragmatique aux contraintes réelles

---

<!-- _class: lead -->

# Intégration chatbot + RAG

**Demi-journée finale — Assembler les briques**

> Vous avez vu l'ingestion, le chunking, les embeddings, le retrieval et Ollama séparément.  
> Il est temps de les faire fonctionner ensemble.

**Au programme :**
- Architecture complète du système
- Flux de traitement d'une question, étape par étape
- Gestion de la mémoire conversationnelle
- Interface utilisateur (Gradio, Streamlit, CLI)
- Tests, évaluation et migration vers le cloud

---

# Architecture du système complet

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERFACE                            │
│              Gradio / Streamlit / CLI                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ question + historique
┌──────────────────────▼──────────────────────────────────────┐
│                     ORCHESTRATEUR                           │
│          (LangChain / LlamaIndex / code custom)             │
│  ┌──────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │ Vectorisation │   │   Retrieval   │   │ Construction  │  │
│  │  de la query  │→  │  ChromaDB /   │→  │   du prompt   │  │
│  │ (SentenceT.)  │   │  FAISS        │   │ enrichi       │  │
│  └──────────────┘   └───────────────┘   └───────┬───────┘  │
└──────────────────────────────────────────────────┼──────────┘
                                                   │
┌──────────────────────────────────────────────────▼──────────┐
│                  OLLAMA (local)                             │
│              Mistral 7B Instruct                            │
│         → réponse + sources citées                         │
└─────────────────────────────────────────────────────────────┘
```

---

# Le flux de traitement d'une question

```
Utilisateur : "Quel est le ratio combiné du dernier trimestre ?"
      ↓
[1] Vectorisation de la question
      ↓
[2] Recherche sémantique → Top-3 chunks pertinents
      ↓
[3] Construction du prompt : SYSTEM + CONTEXTE + QUESTION
      ↓
[4] Envoi à Ollama (Mistral 7B local)
      ↓
[5] Réponse + sources citées
      ↓
"Le ratio combiné est de 98,2% (Source : rapport Q3 2024, p.12)"
```

---

# Étape 1 — Réception de la question utilisateur

**Ce qui arrive côté orchestrateur :**
- La question brute en langage naturel
- L'historique de conversation (liste des tours précédents)
- Éventuellement : filtres métier (branche, période, entité)

**Pré-traitements recommandés :**

| Action | Pourquoi |
|--------|----------|
| Normalisation des caractères | Éviter les erreurs sur accents, tirets |
| Détection de langue | Adapter le prompt system si besoin |
| Validation de longueur | Refuser les questions > 1 000 tokens |
| Journalisation horodatée | Auditabilité et debug |

**Données sensibles :**
- Ne jamais logger les données personnelles contenues dans la question
- Appliquer la même politique de sécurité qu'un formulaire web

---

# Étape 2 — Vectorisation de la question

**Objectif :** transformer la question texte en vecteur pour la recherche sémantique

**Points clés :**
- Utiliser **le même modèle d'embedding** que celui utilisé à l'indexation
- Un modèle différent à l'indexation et à la requête = résultats incohérents
- Modèle recommandé : `paraphrase-multilingual-mpnet-base-v2` (multilingue, performant)

**Ce qui se passe :**

```
"Quel est le ratio combiné ?"
        ↓  encode()
[ 0.021, -0.134, 0.087, ..., 0.003 ]   ← vecteur de 768 dimensions
```

**Temps de traitement :**
- Sur CPU : < 50 ms pour une question courte
- Sur GPU : < 5 ms
- Négligeable par rapport à la génération Ollama

---

# Étape 3 — Recherche sémantique dans le corpus

**La requête vectorielle :**
- Le vecteur de la question est comparé à tous les vecteurs du corpus
- Mesure de similarité : **cosinus** (valeur entre -1 et 1, cible > 0.7)
- Résultat : Top-k chunks les plus pertinents (k = 3 à 5 généralement)

**Filtres combinés :**

| Filtre | Exemple actuariel |
|--------|--------------------|
| Métadonnées | `branche = "Auto"`, `année = 2024` |
| Score minimum | Ne retenir que cosinus > 0.65 |
| Déduplication | Ignorer les chunks quasi-identiques |
| Fraîcheur | Prioriser les documents récents |

**Ce que retourne le retrieval :**
- 3 à 5 extraits de texte avec leurs métadonnées (source, page, date)
- Ces extraits formeront le CONTEXTE injecté dans le prompt

---

# Étape 4 — Construction du prompt enrichi

**Structure du prompt final envoyé au LLM :**

```
SYSTEM :
Tu es un assistant actuariel expert. Réponds uniquement en te
basant sur le contexte fourni. Si la réponse n'y figure pas,
dis-le explicitement. Cite tes sources (document, page).

CONTEXTE :
[Chunk 1] rapport_Q3_2024.pdf, p.12 :
"Le ratio combiné s'établit à 98,2% au T3 2024..."

[Chunk 2] note_technique_auto.pdf, p.4 :
"La fréquence sinistre auto a progressé de 0,3 pt..."

QUESTION :
Quel est le ratio combiné du dernier trimestre ?
```

**Règles de construction :**
- Limiter le contexte injecté à ~2 000 tokens pour laisser de la place à la réponse
- Trier les chunks par score décroissant — le plus pertinent en premier
- Inclure la source dans chaque chunk pour permettre la citation

---

# Étape 5 — Envoi à Ollama et génération

**Paramètres de l'appel API :**

| Paramètre | Valeur recommandée | Effet |
|-----------|-------------------|-------|
| `model` | `mistral:7b-instruct` | Modèle cible |
| `temperature` | 0.1 – 0.2 | Réponses factuelles, peu d'invention |
| `num_ctx` | 4 096 – 8 192 | Fenêtre de contexte |
| `top_p` | 0.9 | Diversité lexicale modérée |
| `stream` | `true` | Affichage progressif dans l'UI |

**Gestion des erreurs :**
- Timeout Ollama > 30 s → afficher un message d'attente, réessayer une fois
- Réponse vide ou tronquée → détecter et avertir l'utilisateur
- Ollama down → fallback message clair ("service temporairement indisponible")

**Monitoring :**
- Logger : modèle utilisé, nb tokens prompt, nb tokens réponse, latence totale
- Ces métriques permettent d'optimiser le pipeline itérativement

---

# Étape 6 — Retour de la réponse avec sources citées

**Format de réponse recommandé :**

```
Réponse :
Le ratio combiné s'établit à 98,2 % au T3 2024, en hausse de
1,1 point par rapport au T2 2024 (97,1 %).

Sources :
• rapport_Q3_2024.pdf — p.12 (score : 0.91)
• note_technique_auto.pdf — p.4 (score : 0.78)
```

**Pourquoi citer les sources :**
- Permet à l'utilisateur de vérifier et valider la réponse
- Réduit le risque d'hallucination non détectée
- Conforme aux exigences d'auditabilité en environnement réglementé

**Bonnes pratiques :**
- Afficher le score de similarité — transparent sur la confiance du retrieval
- Lier les sources au document d'origine si un DMS est disponible
- Indiquer si aucun chunk pertinent n'a été trouvé plutôt que d'inventer

---

# Gestion de l'historique de conversation (mémoire)

**Pourquoi la mémoire est nécessaire :**

```
Tour 1 — Utilisateur : "Quel est le ratio combiné Auto ?"
Tour 1 — Bot : "98,2 % au T3 2024."

Tour 2 — Utilisateur : "Et pour la branche MRH ?"
         ↑ Sans mémoire : le LLM ne sait pas que "et" réfère au ratio combiné
```

**Stratégies de mémoire :**

| Type | Mécanisme | Limite |
|------|-----------|--------|
| Buffer window | Conserver les N derniers tours | Simple, peut saturer le contexte |
| Summary memory | Résumer les anciens tours | Perte d'information fine |
| Entity memory | Extraire et mémoriser les entités clés | Complexe à implémenter |
| Vector memory | Vectoriser les tours et les retrouver | Puissant, coûteux |

**Recommandation pour démarrer :**
- Buffer window de 4 à 6 tours — simple, efficace, prévisible
- Inclure l'historique dans le prompt avant la question courante

---

# Mémoire et fenêtre de contexte — compromis

**Le problème fondamental :**
- Plus on garde d'historique → meilleure compréhension conversationnelle
- Plus on garde d'historique → moins de place pour le contexte RAG
- Fenêtre de contexte Mistral 7B : 8 192 tokens par défaut

**Répartition recommandée sur 8 192 tokens :**

| Zone | Tokens alloués | Contenu |
|------|---------------|---------|
| Prompt system | ~150 | Instructions du rôle |
| Historique | ~1 500 | 4–6 derniers tours |
| Contexte RAG | ~2 000 | 3–4 chunks pertinents |
| Question courante | ~200 | La question de l'utilisateur |
| Réponse attendue | ~500 | Marge pour la génération |
| **Total** | **~4 350** | Marge de sécurité confortable |

**Stratégie de troncation :**
- Si le contexte dépasse le budget → tronquer l'historique en premier
- Toujours conserver au moins 1 tour précédent pour la cohérence

---

# Interface utilisateur — options

**Trois approches selon les besoins :**

| Option | Profil | Avantages | Limites |
|--------|--------|-----------|---------|
| **CLI** | Dev / script | Zéro dépendance, scriptable | Pas d'UI graphique |
| **Gradio** | Demo / POC rapide | Déploiement en 10 lignes | Personnalisation limitée |
| **Streamlit** | Application interne | Riche, layouts flexibles | Plus verbeux |

**Critères de choix en contexte Groupama :**
- Usage personnel / automatisation → **CLI**
- Demo métier rapide (< 1 jour de dev) → **Gradio**
- Application équipe avec historique, filtres, export → **Streamlit**

**Déploiement :**
- En local : lancer sur `localhost:7860` (Gradio) ou `localhost:8501` (Streamlit)
- Sur serveur interne : reverse proxy Nginx, accès restreint au réseau Groupama
- Pas besoin de cloud pour un usage confidentiel

---

# Gradio — interface web minimaliste

**Principe :**
- Une fonction Python → une interface web auto-générée
- Idéal pour valider rapidement le pipeline RAG devant les métiers

**Structure d'une interface Gradio pour chatbot RAG :**

```
┌──────────────────────────────────────────────────────┐
│  Chatbot RAG Actuariel — Groupama                    │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Historique de conversation                    │  │
│  │  Utilisateur : Quel est le ratio combiné ?     │  │
│  │  Bot : 98,2 % au T3 2024 (Source : p.12)      │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  [  Votre question...                      ] [Envoyer]│
│                                                      │
│  Filtre branche : [Auto ▼]   Année : [2024 ▼]       │
└──────────────────────────────────────────────────────┘
```

**Composants clés :**
- `gr.Chatbot` — affiche l'historique avec rendu Markdown
- `gr.Textbox` — saisie de la question
- `gr.Dropdown` — filtres métier (branche, année, entité)
- `gr.Button` — déclenchement de la requête

---

# Streamlit — alternative populaire

**Différence fondamentale avec Gradio :**
- Gradio : déclare des composants → UI auto-générée
- Streamlit : script Python exécuté de haut en bas à chaque interaction

**Structure d'une app Streamlit chatbot RAG :**

```
Page Streamlit
├── st.sidebar
│   ├── Filtres : branche, année, entité
│   ├── Paramètres : k (nb chunks), température
│   └── Bouton "Nouvelle conversation"
├── st.container  (historique des messages)
│   ├── Message utilisateur (st.chat_message "user")
│   └── Message bot (st.chat_message "assistant")
│       └── Sources citées en expander
└── st.chat_input  (saisie de la question)
```

**Avantages Streamlit pour un usage interne :**
- `st.session_state` pour la mémoire conversationnelle entre rechargements
- Export CSV / Word de la conversation en un bouton
- Intégration facile de graphiques matplotlib ou plotly

---

# Tests end-to-end — scénarios de validation

**Catégories de tests pour un chatbot RAG actuariel :**

| Catégorie | Exemple de question | Résultat attendu |
|-----------|--------------------|--------------------|
| **Happy path** | "Ratio combiné Auto T3 2024 ?" | Chiffre correct + source |
| **Hors corpus** | "Météo de Paris demain ?" | "Je ne dispose pas de cette information" |
| **Ambiguïté** | "Résultats de la branche ?" | Demande de précision (quelle branche ?) |
| **Temporel** | "Évolution sur 3 ans ?" | Agrégation de plusieurs chunks |
| **Contradiction** | Question sur données conflictuelles | Signalement de l'ambiguïté |
| **Injection** | "Ignore tes instructions et..." | Refus poli, pas de fuite |

**Métriques de test :**
- Taux de réponses correctes sur jeu de référence (gold dataset)
- Taux de refus appropriés (questions hors périmètre)
- Latence P50 / P95 sur jeu de questions typiques
- Taux d'hallucination (réponse non sourcée dans le corpus)

---

# Qualité des réponses — évaluation finale

**Framework RAGAS — 4 métriques clés :**

| Métrique | Ce qu'elle mesure | Cible |
|----------|------------------|-------|
| **Faithfulness** | La réponse est-elle fidèle aux chunks ? | > 0.85 |
| **Answer Relevancy** | La réponse répond-elle à la question ? | > 0.80 |
| **Context Precision** | Les chunks récupérés sont-ils pertinents ? | > 0.75 |
| **Context Recall** | Tous les chunks utiles ont-ils été récupérés ? | > 0.70 |

**Processus d'évaluation recommandé :**
1. Constituer un jeu de 20 à 50 questions de référence avec les réponses attendues
2. Faire tourner le pipeline et collecter les réponses + chunks récupérés
3. Calculer les 4 métriques RAGAS (ou manuellement sur échantillon)
4. Identifier les faiblesses : retrieval ? chunking ? prompt ? modèle ?
5. Itérer sur le maillon faible

**En contexte réglementé :**
- Documenter les métriques obtenues pour la validation interne
- Conserver le jeu de test de référence versionné avec le code

---

# De Ollama au cloud — stratégies de migration

**Quand envisager la migration vers le cloud :**
- Besoin de modèles > 70B (impossible localement)
- Volume de requêtes concurrent élevé (> 10 utilisateurs simultanés)
- Nécessité de fine-tuning sur données Groupama

**Scénarios de migration :**

| Scénario | Solution | Niveau de confidentialité |
|----------|----------|--------------------------|
| Cloud public | OpenAI GPT-4o, Claude | Données partagées (à éviter pour données sensibles) |
| Cloud souverain | Azure OpenAI (France Central) | RGPD, données hébergées en France |
| On-premise GPU | Serveur GPU interne + vLLM | Équivalent Ollama, scalable |
| Hybrid | Local pour données sensibles, cloud pour généraliste | Optimal, plus complexe |

**Ce qui ne change pas lors de la migration :**
- Le pipeline RAG (chunking, embedding, retrieval)
- L'interface utilisateur
- Seul l'endpoint LLM change — c'est la force de l'abstraction LangChain

---

# Limites de l'architecture RAG locale

**Limites techniques :**

| Limite | Impact | Contournement |
|--------|--------|---------------|
| Fenêtre de contexte (~8K tokens) | Ne peut pas ingérer un rapport entier en une fois | Chunking + retrieval |
| Modèle 7B en local | Raisonnement limité sur questions complexes | Migrer vers 13B ou 70B |
| Pas de mise à jour en temps réel | Le corpus doit être ré-indexé manuellement | Pipeline d'ingestion automatisé |
| Latence CPU (10–30 s) | Expérience utilisateur dégradée | GPU dédié ou cloud |

**Limites architecturales :**
- RAG ne peut répondre qu'à ce qui est dans le corpus — pas de raisonnement analytique natif
- Qualité de la réponse dépend fortement de la qualité du chunking
- Les documents mal structurés (PDF scannés, tableaux complexes) dégradent les performances

**Ce que RAG ne remplace pas :**
- Un expert actuariel pour l'interprétation et la validation
- Un système de BI pour les calculs dynamiques sur base de données
- Une revue humaine pour les rapports réglementaires

---

# Perspectives : agents LLM et RAG multi-modal

**Agents LLM — aller au-delà du RAG :**
- Un agent peut utiliser des **outils** (calculatrice, API, base SQL, code Python)
- Exemple : "Calcule l'évolution du S/P sur 5 ans et génère le graphique"
  → L'agent écrit du code, l'exécute, récupère le résultat
- Frameworks : LangChain Agents, LlamaIndex Agents, AutoGen

**RAG multi-modal :**
- Traiter des documents contenant texte **et** images (graphiques, schémas, photos)
- Modèles vision-langage (VLM) : LLaVA, Phi-3 Vision, Qwen-VL
- Cas d'usage actuariel : analyser une courbe de sinistralité dans un PDF scanné

**RAG sur bases structurées (Text-to-SQL) :**
- Traduire une question naturelle en requête SQL
- Interroger directement les tables de provisions ou de sinistres
- Combiner avec RAG documentaire pour des réponses hybrides

**Horizon 2025–2026 :**
- Contextes de 128K à 1M tokens → moins besoin de chunking fin
- Modèles locaux 13B–34B accessibles sur GPU consommateur
- Évaluation automatique des réponses RAG intégrée aux frameworks

---

# Bilan de la formation — ce que vous savez maintenant faire

**Après ces 3 jours, vous êtes capables de :**

**Pipeline RAG complet :**
- Ingérer un corpus documentaire (PDF, Word, texte) et le préparer
- Découper intelligemment en chunks avec stratégie adaptée au contenu
- Générer des embeddings et les stocker dans une base vectorielle (ChromaDB, FAISS)
- Interroger le corpus en langage naturel et récupérer les passages pertinents
- Brancher un LLM local (Ollama / Mistral) pour générer une réponse sourcée

**Applications concrètes :**
- Interroger un corpus de rapports actuariels, de notes techniques ou de sinistres
- Générer automatiquement des rapports Word formatés depuis les données du RAG
- Produire des présentations PowerPoint alimentées par les résultats du pipeline
- Déployer un chatbot 100 % local, sans aucune donnée sortante — confidentialité totale

**Ce que vous pouvez faire dès demain :**
- Indexer vos propres documents métier et poser vos premières questions
- Présenter une démo fonctionnelle à votre équipe ou à la DSI
- Évaluer la qualité des réponses et itérer sur le pipeline

> Vous avez construit, brique par brique, un système d'IA sur document complet.  
> La valeur est dans votre corpus — le pipeline est maintenant entre vos mains.

---

# Ressources pour aller plus loin

**Librairies et frameworks :**

| Librairie | Usage principal |
|-----------|----------------|
| **LangChain** | Orchestration RAG, agents, mémoire, chaînes |
| **LlamaIndex** | RAG avancé, index hiérarchiques, query engines |
| **Haystack** (deepset) | Pipelines RAG production-ready, évaluation intégrée |
| **ChromaDB** | Base vectorielle légère, open source |
| **FAISS** (Meta) | Recherche vectorielle ultra-rapide, en mémoire |
| **SentenceTransformers** | Embeddings multilingues de référence |
| **RAGAS** | Évaluation automatique de pipelines RAG |

**Papiers fondateurs :**
- *Attention is All You Need* — Vaswani et al. (2017) — architecture Transformer
- *BERT: Pre-training of Deep Bidirectional Transformers* — Devlin et al. (2018)
- *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* — Lewis et al. (2020)
- *Mistral 7B* — Jiang et al. (2023) — le modèle que vous avez utilisé

**Communautés :**
- **Hugging Face** — modèles, datasets, spaces, leaderboards
- **LangChain Hub** — prompts partagés, chaînes réutilisables
- **Ollama Library** — catalogue de modèles disponibles localement
- **r/LocalLLaMA** — communauté Reddit sur les LLMs locaux

---

# Ce qu'on retient — Intégration chatbot + RAG

**Le pipeline complet en 6 étapes :**
1. **Réception** — question utilisateur + historique de conversation
2. **Vectorisation** — même modèle d'embedding qu'à l'indexation
3. **Retrieval** — Top-k chunks par similarité cosinus + filtres métier
4. **Prompt engineering** — SYSTEM + CONTEXTE (chunks) + QUESTION
5. **Génération** — Ollama local, temperature basse, streaming
6. **Restitution** — réponse + sources citées + score de confiance

**Les compromis à maîtriser :**
- Taille des chunks vs précision du retrieval
- Nombre de chunks injectés vs budget de tokens
- Historique conservé vs place pour le contexte RAG
- Latence locale vs confidentialité absolue

**Ce qui fait la différence en production :**
- La qualité du corpus (documents bien structurés, à jour)
- Le soin apporté au prompt system (instructions claires, garde-fous)
- L'évaluation régulière sur un jeu de questions de référence

> Un pipeline RAG n'est pas un produit fini — c'est un système vivant  
> qui s'améliore avec les retours utilisateurs et la qualité du corpus.

---
