
from pprint import pprint
from glob import glob
import shutil
from pathlib import Path
# from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from typing import Any
import ollama

MODELE_EMBED  = "bge-m3"  
DB_DIR = Path('./db_tp')

if DB_DIR.exists():
    shutil.rmtree(DB_DIR)

def embed_texts(textes: list[str]) -> list[list[float]]:
    """Encode une liste de textes en vecteurs via bge-m3 (Ollama)."""
    res = ollama.embed(model=MODELE_EMBED, input=textes)
    return res["embeddings"]
 
def embed_one(texte: str) -> list[float]:
    """Encode un seul texte ; renvoie un unique vecteur."""
    return embed_texts([texte])[0]




def main():
    # start ingestion
    all_md = glob('./corpus_tp/*.md')
    noms     = [f for f in all_md]
    textes = []
    for nom in noms:
        with open(nom, 'r') as f:
            textes.append(f.read())

    # start chunking

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, chunk_overlap=30,
        separators=["## ", "\n\n", "\n", " ", ""],
    )   

    client = chromadb.PersistentClient(path=str(DB_DIR))

    collection = client.get_or_create_collection(
        "corpus_rag", metadata={"hnsw:space": "cosine"}
    )

    tous_chunks, tous_ids, tous_metadatas = [], [], []
    for nom, texte in zip(noms, textes):
        for i, chunk in enumerate(splitter.split_text(texte)):
            tous_chunks.append(chunk)
            tous_ids.append(f"{nom}__{i:02d}")
            tous_metadatas.append({"source": nom, "chunk_index": i})
    
    print(f"Nombre total de chunks : {len(tous_chunks)}")

    collection.add(
        ids=tous_ids,
        documents=tous_chunks,
        embeddings=embed_texts(tous_chunks),
        metadatas=tous_metadatas,
    )


if __name__=='__main__':
    main()
