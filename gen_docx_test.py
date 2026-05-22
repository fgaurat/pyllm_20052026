#!/usr/bin/env python3
"""
gen_docx_test.py
================

Génère un document Word (.docx) de test dans ./corpus_tp pour le corpus
d'ingestion RAG : prose courante + tableaux variés.

Usage :
    uv run --with python-docx python gen_docx_test.py
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


OUT_PATH = Path(__file__).parent / "corpus_tp" / "test_document.docx"

HEADER_BG = "34495E"
ALT_ROW_BG = "ECF0F1"


def _shade_cell(cell, hex_color: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def add_table(doc: Document, data: list[list[str]]) -> None:
    table = doc.add_table(rows=len(data), cols=len(data[0]))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for col_idx, header in enumerate(data[0]):
        cell = table.rows[0].cells[col_idx]
        cell.text = ""
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(header)
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)
        _shade_cell(cell, HEADER_BG)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    for row_idx, row in enumerate(data[1:], start=1):
        for col_idx, value in enumerate(row):
            cell = table.rows[row_idx].cells[col_idx]
            cell.text = ""
            para = cell.paragraphs[0]
            run = para.add_run(value)
            run.font.size = Pt(10)
            if row_idx % 2 == 0:
                _shade_cell(cell, ALT_ROW_BG)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    doc.add_paragraph()


def build() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()

    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    core = doc.core_properties
    core.title = "Document de test — Corpus RAG actuariel"
    core.author = "Formation RAG Groupama"
    core.subject = "Exemple .docx pour ingestion multi-format"

    doc.add_heading("Document de test — Corpus RAG", level=0)
    doc.add_heading("Exemple .docx pour le pipeline d'ingestion", level=2)

    doc.add_paragraph(
        "Ce document Word est généré automatiquement pour alimenter le "
        "corpus de test du pipeline RAG. Il complète les PDF déjà présents "
        "dans le dossier corpus_tp en proposant un format bureautique "
        "courant, avec un mélange de prose et de tableaux."
    )
    doc.add_paragraph(
        "L'objectif est de valider la chaîne d'extraction sur des "
        "documents .docx : préservation de la structure des titres, "
        "extraction correcte des tableaux et conservation du texte courant."
    )

    doc.add_heading("1. Métadonnées du document", level=1)
    add_table(doc, [
        ["Champ", "Valeur"],
        ["Titre", "Document de test — Corpus RAG"],
        ["Version", "1.0"],
        ["Date", "22 mai 2026"],
        ["Format", "Microsoft Word (.docx, Office Open XML)"],
        ["Langue", "Français"],
        ["Auteur", "Formation RAG Groupama"],
    ])

    doc.add_heading("2. Bilan comptable simplifié", level=1)
    doc.add_paragraph(
        "Présentation simplifiée du bilan d'une compagnie d'assurance "
        "fictive au 31 décembre 2025. Montants en milliers d'euros."
    )
    add_table(doc, [
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
    ])

    doc.add_heading("3. Méthodologie de provisionnement", level=1)
    for paragraph in [
        "Le provisionnement technique en assurance non-vie repose sur "
        "l'estimation des engagements futurs de l'assureur envers ses "
        "assurés. Les méthodes les plus répandues sont Chain-Ladder, "
        "Bornhuetter-Ferguson et les modèles linéaires généralisés (GLM).",
        "La méthode Chain-Ladder exploite la régularité du développement "
        "des sinistres pour projeter les paiements futurs à partir d'un "
        "triangle de liquidation. Sa simplicité en a fait un standard "
        "professionnel, malgré ses limites sur les portefeuilles atypiques.",
        "L'approche Bornhuetter-Ferguson combine Chain-Ladder et une "
        "charge ultime a priori issue de l'expérience tarifaire. Elle est "
        "particulièrement utile pour les exercices récents.",
        "Les GLM permettent de modéliser explicitement la distribution "
        "des coûts de sinistres et d'intégrer des variables explicatives. "
        "Ils sont aujourd'hui le socle des approches Solvabilité II pour "
        "le calcul du SCR non-vie.",
    ]:
        doc.add_paragraph(paragraph)

    doc.add_heading("4. Comparatif de modèles open weights", level=1)
    doc.add_paragraph(
        "Benchmarks publics 1er trimestre 2026, modèles instruct, "
        "quantisation Q4_K_M."
    )
    add_table(doc, [
        ["Modèle", "Paramètres", "Context", "MMLU", "MT-Bench", "VRAM Q4"],
        ["Llama 3.1 8B", "8 B", "128k", "68,4", "8,1", "6,1 Go"],
        ["Mistral 7B v0.3", "7 B", "32k", "62,5", "7,3", "5,4 Go"],
        ["Qwen 2.5 7B", "7 B", "128k", "74,2", "8,4", "5,8 Go"],
        ["Gemma 2 9B", "9 B", "8k", "71,3", "8,0", "6,9 Go"],
        ["Phi-3.5 Mini", "3,8 B", "128k", "69,0", "8,3", "2,9 Go"],
        ["Mixtral 8×7B", "47 B (MoE)", "32k", "70,6", "8,3", "26,4 Go"],
        ["Llama 3.1 70B", "70 B", "128k", "82,4", "9,0", "40,2 Go"],
    ])

    doc.add_heading("5. Glossaire d'acronymes", level=1)
    add_table(doc, [
        ["Acronyme", "Signification"],
        ["SCR", "Solvency Capital Requirement"],
        ["BEL", "Best Estimate Liabilities"],
        ["ORSA", "Own Risk and Solvency Assessment"],
        ["GLM", "Generalized Linear Model"],
        ["RAG", "Retrieval-Augmented Generation"],
        ["LLM", "Large Language Model"],
        ["OCR", "Optical Character Recognition"],
    ])

    doc.add_paragraph()
    end = doc.add_paragraph("— Fin du document de test —")
    end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    end.runs[0].italic = True
    end.runs[0].font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    doc.save(OUT_PATH)
    print(f"✓ DOCX généré : {OUT_PATH}")
    print(f"  Taille : {OUT_PATH.stat().st_size / 1024:.1f} Ko")


if __name__ == "__main__":
    build()
