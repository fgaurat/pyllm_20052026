"""
tp_retrieval_docx.py
====================

Reprend la logique de tp_retrieval.py et exécute les quatre questions
d'évaluation du RAG sur le corpus_tp. Pour chaque question :
  1. récupère les top-k chunks via Chroma + embeddings bge-m3
  2. interroge Mistral via Ollama avec les chunks comme contexte
  3. consigne question / chunks / réponse dans un document Word

Usage :
    uv run --with python-docx python tp_retrieval_docx.py
"""

import json
import re
from datetime import datetime
from pathlib import Path

import chromadb
import ollama
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

DB_DIR = Path("./db_tp")
OUT_PATH = Path("./reponses_rag.docx")

MODELE_EMBED = "bge-m3"
MODELE_LLM = "llama3.2:3b"
TOP_K = 3

SYSTEM_PROMPT = """Tu es un assistant expert en plantes d'intérieur.
Réponds à la question en te basant UNIQUEMENT sur le contexte fourni.
Si la réponse n'est pas dans le contexte, dis-le explicitement.
Cite les sources utilisées entre crochets (ex : [doc05_fougere]).
"""

QUESTIONS = [
    "Quelles sont les conditions d'exposition et d'arrosage idéales pour un ficus d'intérieur ?",
    "Comment distinguer un manque d'eau d'un excès d'arrosage chez une plante verte d'intérieur ?",
    "Quelles plantes recommandées pour purifier l'air sont également non toxiques pour les chats ?",
    "Quel calendrier de rempotage et de fertilisation suivre sur une année pour une plante à croissance rapide ?",
]


# --------------------------------------------------------------------------- #
#  Retrieval (identique à tp_retrieval.py)                                    #
# --------------------------------------------------------------------------- #
def embed_texts(textes: list[str]) -> list[list[float]]:
    return ollama.embed(model=MODELE_EMBED, input=textes)["embeddings"]


def embed_one(texte: str) -> list[float]:
    return embed_texts([texte])[0]


def retriever(collection, requete: str, k: int = TOP_K) -> list[dict]:
    vecteur = [embed_one(requete)]
    res = collection.query(
        query_embeddings=vecteur,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "texte": doc,
            "source": (meta or {}).get("source", "n/a"),
            "score": round(1 - dist, 4),
        }
        for doc, meta, dist in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
        )
    ]


def interroger_llm(chunks: list[dict], requete: str) -> str:
    response = ollama.chat(
        model=MODELE_LLM,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(chunks, ensure_ascii=False) + " " + requete},
        ],
        options={"temperature": 0},
    )
    return response.message.content


# --------------------------------------------------------------------------- #
#  Rendu markdown → Word                                                       #
# --------------------------------------------------------------------------- #
# Les LLMs renvoient souvent du markdown (titres, gras, listes…). Sans
# interprétation, ces caractères apparaissent bruts dans le .docx. On gère
# ici le sous-ensemble courant.

_INLINE_RE = re.compile(
    r"(\*\*(?P<b1>[^*]+)\*\*|__(?P<b2>[^_]+)__|"
    r"\*(?P<i1>[^*]+)\*|_(?P<i2>[^_]+)_|`(?P<code>[^`]+)`)"
)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
_NUMBERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
_BLOCK_START_RE = re.compile(r"^(#{1,6}\s|```|\s*[-*+]\s|\s*\d+\.\s)")


def _add_inline(paragraph, text: str) -> None:
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        gd = m.groupdict()
        if gd["b1"] or gd["b2"]:
            paragraph.add_run(gd["b1"] or gd["b2"]).bold = True
        elif gd["i1"] or gd["i2"]:
            paragraph.add_run(gd["i1"] or gd["i2"]).italic = True
        elif gd["code"]:
            run = paragraph.add_run(gd["code"])
            run.font.name = "Consolas"
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def add_markdown(doc: Document, text: str, base_level: int = 3) -> None:
    """Rend un texte markdown dans le document. `base_level` = niveau de titre
    pour `# ` (les sous-titres descendent à partir de là)."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()

        if not line.strip():
            i += 1
            continue

        m = _HEADING_RE.match(line)
        if m:
            level = min(base_level + len(m.group(1)) - 1, 9)
            doc.add_heading(m.group(2), level=level)
            i += 1
            continue

        if line.lstrip().startswith("```"):
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            p = doc.add_paragraph()
            run = p.add_run("\n".join(code_lines))
            run.font.name = "Consolas"
            run.font.size = Pt(10)
            continue

        if _BULLET_RE.match(line):
            while i < len(lines):
                m = _BULLET_RE.match(lines[i].rstrip())
                if not m:
                    break
                p = doc.add_paragraph(style="List Bullet")
                _add_inline(p, m.group(1))
                i += 1
            continue

        if _NUMBERED_RE.match(line):
            while i < len(lines):
                m = _NUMBERED_RE.match(lines[i].rstrip())
                if not m:
                    break
                p = doc.add_paragraph(style="List Number")
                _add_inline(p, m.group(1))
                i += 1
            continue

        para_lines = [line]
        i += 1
        while (i < len(lines)
               and lines[i].strip()
               and not _BLOCK_START_RE.match(lines[i])):
            para_lines.append(lines[i].rstrip())
            i += 1
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _add_inline(p, " ".join(para_lines))


# --------------------------------------------------------------------------- #
#  Génération du document Word                                                #
# --------------------------------------------------------------------------- #
def init_document() -> Document:
    doc = Document()

    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    doc.core_properties.title = "Évaluation RAG — Plantes d'intérieur"
    doc.core_properties.author = "Formation RAG Groupama"

    doc.add_heading("Évaluation RAG — Plantes d'intérieur", level=0)
    intro = doc.add_paragraph()
    intro.add_run(
        f"Pipeline : Chroma (cosine) + embeddings {MODELE_EMBED} + génération {MODELE_LLM} "
        f"via Ollama. Top-k = {TOP_K}."
    )
    horodatage = doc.add_paragraph()
    horodatage.add_run(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}."
    ).italic = True

    return doc


def ajouter_section(doc: Document, numero: int, question: str,
                    chunks: list[dict], reponse: str) -> None:
    doc.add_heading(f"Question {numero}", level=1)

    p_q = doc.add_paragraph()
    p_q.add_run("Question : ").bold = True
    p_q.add_run(question)

    doc.add_heading(f"Chunks récupérés (top-{TOP_K})", level=2)
    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, label in enumerate(["#", "Score", "Extrait"]):
        cell = hdr[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(label)
        run.bold = True

    for i, chunk in enumerate(chunks, 1):
        row = table.add_row().cells
        row[0].text = str(i)
        row[1].text = str(chunk["score"])
        extrait = chunk["texte"]
        if len(extrait) > 600:
            extrait = extrait[:600] + " […]"
        row[2].text = extrait

    doc.add_heading(f"Réponse de {MODELE_LLM}", level=2)
    add_markdown(doc, reponse, base_level=3)

    doc.add_paragraph()


def cloturer(doc: Document) -> None:
    fin = doc.add_paragraph("— Fin du rapport —")
    fin.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fin.runs[0]
    run.italic = True
    run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)


# --------------------------------------------------------------------------- #
#  Main                                                                       #
# --------------------------------------------------------------------------- #
def main() -> None:
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_or_create_collection(
        "corpus_rag", metadata={"hnsw:space": "cosine"}
    )

    doc = init_document()

    for i, question in enumerate(QUESTIONS, 1):
        print(f"\n[{i}/{len(QUESTIONS)}] {question}")
        chunks = retriever(collection, question, k=TOP_K)
        print(f"  → {len(chunks)} chunks récupérés")
        reponse = interroger_llm(chunks, question)
        print(f"  → réponse {MODELE_LLM} : {len(reponse)} caractères")
        ajouter_section(doc, i, question, chunks, reponse)

    cloturer(doc)
    doc.save(OUT_PATH)
    print(f"\n✓ Document généré : {OUT_PATH.resolve()}")
    print(f"  Taille : {OUT_PATH.stat().st_size / 1024:.1f} Ko")


if __name__ == "__main__":
    main()
