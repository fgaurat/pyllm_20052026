import chromadb
import ollama
import sys
from pathlib import Path
from pprint import pprint
import json

DB_DIR = Path('./db_tp')
MODELE_EMBED  = "bge-m3"  

TOP_K = 3


def embed_texts(textes: list[str]) -> list[list[float]]:
    """Encode une liste de textes en vecteurs via bge-m3 (Ollama)."""
    res = ollama.embed(model=MODELE_EMBED, input=textes)
    return res["embeddings"]
 
def embed_one(texte: str) -> list[float]:
    """Encode un seul texte ; renvoie un unique vecteur."""
    return embed_texts([texte])[0]


def retriever(collection,requete: str, k: int = TOP_K) -> list[dict]:
    """Retourne les k chunks les plus similaires à la requête."""
    vecteur = [embed_one(requete)]
    res = collection.query(
        query_embeddings=vecteur,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {
            "texte":  doc,
            # "source": meta["source"],
            "score":  round(1 - dist, 4),
        }
        for doc, meta, dist in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
        )
    ]



def main():
    # requete = "Comment soigner une fougère dont les frondes brunissent ?"
    requete = "Comment peigner un poney ?"
    client     = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_or_create_collection(
        "corpus_rag", metadata={"hnsw:space": "cosine"}
    )
    chunks_retrouves = retriever(collection,requete, k=TOP_K)
    print(50*"-")
    pprint(chunks_retrouves)
    print(50*"-")
    pprint(f"Requête : {requete}\n")
    pprint(f"Chunks retrouvés : {chunks_retrouves}\n")

    # sys.exit()
    response = ollama.chat(model='mistral', messages=[
        {
            'role': 'system',
            'content': """Tu es un assistant expert en plantes d'intérieur.
Réponds à la question en te basant UNIQUEMENT sur le contexte fourni.
Si la réponse n'est pas dans le contexte, dis-le explicitement.
Cite les sources utilisées entre crochets (ex : [doc05_fougere]).
            """,
        },
    {

        'role': 'user',
        'content': json.dumps(chunks_retrouves)+" "+requete,
    },
    ])
    # print(response['message']['content'])
    # or access fields directly from the response object
    print(response.message.content)


if __name__=='__main__':
    main()
