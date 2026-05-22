#!/usr/bin/env python3
"""
gen_pdf_ocr_test.py
===================

Génère un PDF de 10 pages dans ./corpus_tp pour tester un pipeline OCR :
texte courant + tableaux variés (financiers, techniques, mixtes).

Usage :
    uv run --with reportlab python gen_pdf_ocr_test.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


OUT_PATH = Path(__file__).parent / "corpus_tp" / "test_ocr_tables.pdf"


def styled_table(data, col_widths=None, header_bg=colors.HexColor("#34495e")):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.whitesmoke, colors.HexColor("#ecf0f1")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ]
        )
    )
    return t


def build():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Document de test OCR — Tableaux",
        author="Formation RAG Groupama",
    )

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = ParagraphStyle(
        "body", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=8
    )

    story = []

    # --------------------------------------------------------------------- #
    # Page 1 — Couverture + intro                                           #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("Document de test OCR", h1))
    story.append(Paragraph("Corpus de tableaux pour pipeline RAG actuariel", h2))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Ce document a été généré automatiquement pour tester l'extraction "
        "de texte et de tableaux par un moteur OCR (Tesseract, docling, "
        "Azure Document Intelligence, etc.). Il contient dix pages mêlant "
        "paragraphes courants, tableaux financiers, techniques et démographiques.",
        body,
    ))
    story.append(Paragraph(
        "L'objectif est de vérifier la qualité de l'extraction sur des "
        "structures hétérogènes : tableaux à colonnes étroites, valeurs "
        "numériques avec séparateurs, en-têtes fusionnés conceptuellement, "
        "et alternance texte/tableau dans la même page.",
        body,
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Métadonnées du document", h2))
    story.append(styled_table(
        [
            ["Champ", "Valeur"],
            ["Titre", "Document de test OCR — Tableaux"],
            ["Version", "1.0"],
            ["Date", "22 mai 2026"],
            ["Pages", "10"],
            ["Langue", "Français"],
            ["Encodage", "UTF-8"],
            ["Format", "PDF/A compatible"],
        ],
        col_widths=[5 * cm, 10 * cm],
    ))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 2 — Bilan comptable simplifié                                    #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("1. Bilan comptable au 31/12/2025", h1))
    story.append(Paragraph(
        "Présentation simplifiée du bilan d'une compagnie d'assurance "
        "fictive. Les montants sont exprimés en milliers d'euros.",
        body,
    ))
    story.append(styled_table(
        [
            ["Poste", "2024 (k€)", "2025 (k€)", "Variation"],
            ["Immobilisations incorporelles", "12 450", "13 820", "+11,0 %"],
            ["Immobilisations corporelles", "84 300", "86 100", "+2,1 %"],
            ["Placements financiers", "1 245 600", "1 312 400", "+5,4 %"],
            ["Créances", "76 200", "82 050", "+7,7 %"],
            ["Disponibilités", "42 800", "38 900", "-9,1 %"],
            ["Total actif", "1 461 350", "1 533 270", "+4,9 %"],
            ["Capitaux propres", "412 000", "438 500", "+6,4 %"],
            ["Provisions techniques", "956 700", "998 200", "+4,3 %"],
            ["Dettes", "92 650", "96 570", "+4,2 %"],
            ["Total passif", "1 461 350", "1 533 270", "+4,9 %"],
        ],
        col_widths=[7 * cm, 3 * cm, 3 * cm, 3 * cm],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Le total bilanciel progresse de 4,9 % sur l'exercice, porté "
        "principalement par la valorisation du portefeuille de placements.",
        body,
    ))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 3 — Tarification automobile par tranche d'âge                    #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("2. Grille tarifaire automobile 2026", h1))
    story.append(Paragraph(
        "Prime annuelle de référence (formule tous risques, véhicule de "
        "catégorie B, conducteur sans malus, zone géographique 3).",
        body,
    ))
    story.append(styled_table(
        [
            ["Tranche d'âge", "Prime H (€)", "Prime F (€)", "Coef. malus max",
             "Réduction max"],
            ["18 – 21 ans", "1 890", "1 720", "3,50", "0 %"],
            ["22 – 25 ans", "1 420", "1 290", "2,80", "10 %"],
            ["26 – 30 ans", "980", "920", "2,50", "20 %"],
            ["31 – 40 ans", "740", "710", "2,50", "35 %"],
            ["41 – 50 ans", "680", "650", "2,50", "50 %"],
            ["51 – 60 ans", "650", "620", "2,50", "50 %"],
            ["61 – 70 ans", "720", "690", "2,50", "50 %"],
            ["71 – 80 ans", "890", "850", "2,50", "40 %"],
            ["81 ans et +", "1 150", "1 100", "2,50", "30 %"],
        ],
        col_widths=[3.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm, 3 * cm],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Les écarts homme/femme sont conservés à titre historique mais "
        "ne sont plus appliqués en tarification effective depuis 2012 "
        "(arrêt Test-Achats de la CJUE, 1er mars 2011).",
        body,
    ))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 4 — Texte courant (longue prose)                                 #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("3. Méthodologie de provisionnement", h1))
    paragraphs = [
        "Le provisionnement technique en assurance non-vie repose sur "
        "l'estimation des engagements futurs de l'assureur envers ses "
        "assurés. Cette estimation s'appuie sur des méthodes actuarielles "
        "éprouvées, dont les plus répandues sont la méthode Chain-Ladder, "
        "la méthode Bornhuetter-Ferguson et les approches GLM (modèles "
        "linéaires généralisés).",
        "La méthode Chain-Ladder, introduite dans les années 1970, "
        "exploite la régularité du développement des sinistres pour "
        "projeter les paiements futurs à partir d'un triangle de "
        "liquidation. Sa simplicité de mise en œuvre en a fait un "
        "standard de la profession, malgré ses limites lorsque le "
        "portefeuille présente des sinistres atypiques ou des "
        "changements de processus de gestion.",
        "L'approche Bornhuetter-Ferguson combine l'estimation Chain-Ladder "
        "avec une charge ultime a priori, généralement issue de "
        "l'expérience tarifaire. Elle est particulièrement utile pour "
        "les exercices récents, où la part de sinistres déjà déclarés "
        "reste faible et où la projection pure Chain-Ladder serait "
        "instable.",
        "Les modèles GLM, plus sophistiqués, permettent de modéliser "
        "explicitement la distribution des coûts de sinistres et "
        "d'intégrer des variables explicatives (zone, type de garantie, "
        "ancienneté du contrat). Ils sont aujourd'hui le socle des "
        "approches Solvabilité II pour le calcul du SCR non-vie.",
        "Le choix de la méthode dépend de plusieurs facteurs : "
        "profondeur de l'historique disponible, homogénéité du "
        "portefeuille, stabilité des processus de gestion, et exigences "
        "réglementaires applicables. Une bonne pratique consiste à "
        "croiser plusieurs méthodes pour borner l'incertitude sur "
        "l'estimation finale.",
    ]
    for p in paragraphs:
        story.append(Paragraph(p, body))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 5 — Triangle de liquidation                                      #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("4. Triangle de liquidation (paiements cumulés)", h1))
    story.append(Paragraph(
        "Triangle de liquidation des sinistres de la branche automobile, "
        "par exercice de survenance et année de développement. Montants "
        "en milliers d'euros.",
        body,
    ))
    story.append(styled_table(
        [
            ["Surv. / Dév.", "0", "1", "2", "3", "4", "5"],
            ["2020", "12 450", "21 800", "26 100", "27 950", "28 700", "28 950"],
            ["2021", "13 200", "22 950", "27 400", "29 200", "29 950", ""],
            ["2022", "14 100", "24 350", "29 050", "30 980", "", ""],
            ["2023", "15 050", "25 880", "30 720", "", "", ""],
            ["2024", "16 200", "27 600", "", "", "", ""],
            ["2025", "17 350", "", "", "", "", ""],
        ],
        col_widths=[3 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm,
                    2.2 * cm],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Coefficients de passage Chain-Ladder", h2))
    story.append(styled_table(
        [
            ["Passage", "f₀→₁", "f₁→₂", "f₂→₃", "f₃→₄", "f₄→₅"],
            ["Valeur", "1,7345", "1,1923", "1,0658", "1,0259", "1,0087"],
        ],
        col_widths=[3 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm],
    ))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 6 — Tableau démographique                                        #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("5. Pyramide des assurés par région", h1))
    story.append(Paragraph(
        "Répartition du portefeuille au 31/12/2025 (nombre de contrats "
        "actifs, toutes branches confondues).",
        body,
    ))
    story.append(styled_table(
        [
            ["Région", "< 30 ans", "30–49 ans", "50–64 ans", "65+ ans", "Total"],
            ["Île-de-France", "42 380", "68 920", "39 450", "28 110", "178 860"],
            ["Auvergne-Rhône-Alpes", "28 950", "52 480", "31 200", "24 890", "137 520"],
            ["PACA", "19 220", "38 700", "26 850", "22 410", "107 180"],
            ["Nouvelle-Aquitaine", "16 480", "33 950", "24 100", "20 880", "95 410"],
            ["Occitanie", "17 320", "34 280", "23 890", "20 050", "95 540"],
            ["Hauts-de-France", "21 100", "39 750", "23 480", "17 920", "102 250"],
            ["Grand Est", "18 650", "35 200", "22 980", "18 480", "95 310"],
            ["Bretagne", "12 480", "26 920", "18 100", "15 720", "73 220"],
            ["Autres régions", "32 100", "61 240", "39 280", "31 950", "164 570"],
            ["Total France", "208 680", "391 440", "249 330", "200 410", "1 049 860"],
        ],
        col_widths=[5 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.4 * cm],
    ))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 7 — Texte technique court + petit tableau                        #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("6. Architecture du pipeline RAG", h1))
    story.append(Paragraph(
        "Le pipeline RAG (Retrieval-Augmented Generation) déployé dans "
        "le cadre de ce projet repose sur cinq composants principaux : "
        "ingestion, chunking, embedding, indexation vectorielle et "
        "génération. Chaque composant peut être instrumenté "
        "indépendamment pour mesurer la qualité de l'ensemble.",
        body,
    ))
    story.append(styled_table(
        [
            ["Composant", "Outil retenu", "Version", "Hébergement"],
            ["Ingestion", "docling", "2.95", "On-premise"],
            ["Chunking", "LangChain RecursiveSplitter", "0.3.x", "On-premise"],
            ["Embedding", "BGE-M3 (FlagOpen)", "1.5", "On-premise GPU"],
            ["Vector store", "Qdrant", "1.11", "Cluster interne"],
            ["LLM", "Mistral 7B Instruct", "v0.3", "Ollama local"],
            ["Re-ranker", "BGE-reranker-v2-m3", "1.0", "On-premise GPU"],
            ["Orchestration", "LangGraph", "0.2", "On-premise"],
        ],
        col_widths=[4 * cm, 5 * cm, 2 * cm, 4 * cm],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "L'ensemble tourne dans un environnement isolé sans accès "
        "internet, conformément aux exigences de confidentialité des "
        "données actuarielles manipulées.",
        body,
    ))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 8 — Comparatif de modèles                                        #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("7. Comparatif de modèles open weights", h1))
    story.append(Paragraph(
        "Benchmarks publics au 1er trimestre 2026, modèles instruct, "
        "quantisation Q4_K_M pour comparaison équitable.",
        body,
    ))
    story.append(styled_table(
        [
            ["Modèle", "Paramètres", "Context", "MMLU", "HumanEval",
             "MT-Bench", "VRAM Q4"],
            ["Llama 3.1 8B", "8 B", "128k", "68,4", "62,2", "8,1", "6,1 Go"],
            ["Mistral 7B v0.3", "7 B", "32k", "62,5", "30,5", "7,3", "5,4 Go"],
            ["Qwen 2.5 7B", "7 B", "128k", "74,2", "57,9", "8,4", "5,8 Go"],
            ["Gemma 2 9B", "9 B", "8k", "71,3", "40,2", "8,0", "6,9 Go"],
            ["Phi-3.5 Mini", "3,8 B", "128k", "69,0", "62,8", "8,3", "2,9 Go"],
            ["Mixtral 8×7B", "47 B (MoE)", "32k", "70,6", "40,2", "8,3", "26,4 Go"],
            ["Llama 3.1 70B", "70 B", "128k", "82,4", "80,5", "9,0", "40,2 Go"],
        ],
        col_widths=[3.5 * cm, 2.2 * cm, 1.8 * cm, 1.5 * cm, 2 * cm, 2 * cm,
                    2 * cm],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Les modèles MoE comme Mixtral offrent un excellent compromis "
        "performance/coût en inférence, mais nécessitent que l'ensemble "
        "des experts soient chargés en VRAM même si une fraction "
        "seulement est activée par token.",
        body,
    ))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 9 — Sinistralité par garantie                                    #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("8. Sinistralité par garantie — Exercice 2025", h1))
    story.append(Paragraph(
        "Fréquence et coût moyen observés sur le portefeuille multirisque "
        "habitation, échantillon 100 % France métropolitaine.",
        body,
    ))
    story.append(styled_table(
        [
            ["Garantie", "Nb sinistres", "Fréquence", "Coût moyen (€)",
             "Charge totale (k€)"],
            ["Dégât des eaux", "48 920", "4,82 %", "1 245", "60 905"],
            ["Incendie", "3 850", "0,38 %", "8 920", "34 342"],
            ["Vol", "12 480", "1,23 %", "2 850", "35 568"],
            ["Bris de glace", "22 100", "2,18 %", "485", "10 719"],
            ["Catastrophes naturelles", "6 720", "0,66 %", "4 280", "28 762"],
            ["Responsabilité civile", "9 350", "0,92 %", "1 920", "17 952"],
            ["Tempête / grêle", "14 280", "1,41 %", "2 150", "30 702"],
            ["Total", "117 700", "11,60 %", "1 868", "218 950"],
        ],
        col_widths=[4.5 * cm, 2.8 * cm, 2.3 * cm, 2.8 * cm, 3 * cm],
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Le dégât des eaux reste le sinistre dominant en fréquence, mais "
        "l'incendie concentre le coût moyen le plus élevé. Les "
        "événements climatiques (cat-nat, tempête) progressent "
        "significativement par rapport à l'exercice précédent.",
        body,
    ))
    story.append(PageBreak())

    # --------------------------------------------------------------------- #
    # Page 10 — Annexes & glossaire compact                                 #
    # --------------------------------------------------------------------- #
    story.append(Paragraph("9. Annexes — Glossaire d'acronymes", h1))
    story.append(styled_table(
        [
            ["Acronyme", "Signification"],
            ["SCR", "Solvency Capital Requirement"],
            ["MCR", "Minimum Capital Requirement"],
            ["BEL", "Best Estimate Liabilities"],
            ["ORSA", "Own Risk and Solvency Assessment"],
            ["IFRS 17", "International Financial Reporting Standard 17"],
            ["GLM", "Generalized Linear Model"],
            ["LDA", "Loss Distribution Approach"],
            ["VaR", "Value at Risk"],
            ["TVaR", "Tail Value at Risk"],
            ["RAG", "Retrieval-Augmented Generation"],
            ["LLM", "Large Language Model"],
            ["OCR", "Optical Character Recognition"],
            ["PDF", "Portable Document Format"],
        ],
        col_widths=[3 * cm, 12 * cm],
    ))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("10. Contacts", h1))
    story.append(styled_table(
        [
            ["Rôle", "Nom", "Email", "Téléphone"],
            ["Chef de projet", "Marie Dupont", "m.dupont@example.fr", "01 23 45 67 89"],
            ["Actuaire référent", "Jean Martin", "j.martin@example.fr", "01 23 45 67 90"],
            ["Data scientist", "Sophie Lambert", "s.lambert@example.fr", "01 23 45 67 91"],
            ["DPO", "Pierre Rousseau", "dpo@example.fr", "01 23 45 67 92"],
        ],
        col_widths=[3.5 * cm, 3.5 * cm, 5 * cm, 3 * cm],
    ))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "— Fin du document de test —",
        ParagraphStyle("end", parent=body, alignment=1, textColor=colors.grey),
    ))

    doc.build(story)
    print(f"✓ PDF généré : {OUT_PATH}")
    print(f"  Taille : {OUT_PATH.stat().st_size / 1024:.1f} Ko")


if __name__ == "__main__":
    build()
