#!/usr/bin/env python3
"""
ollama_inspect_manifest.py
==========================

Inspecte un modèle Ollama sur le registre OCI (registry.ollama.ai) et
affiche toutes les informations utiles : manifest, URLs des blobs
(config + layers), digests SHA256, tailles, media types.

**Ne télécharge rien** — uniquement le manifest JSON (quelques Ko) pour
en extraire les métadonnées. Utile pour :
- préparer une liste d'URLs à télécharger ailleurs (curl, wget, navigateur)
- vérifier la taille totale d'un modèle avant de le tirer
- diagnostiquer un blocage réseau

Usage
-----
    python ollama_inspect_manifest.py https://www.ollama.com/library/mistral-small3.2
    python ollama_inspect_manifest.py mistral-small3.2:24b
    python ollama_inspect_manifest.py mistral --tag 7b
    python ollama_inspect_manifest.py mistral --json   # sortie brute

Dépendances : uniquement la lib standard (urllib). Aucune install.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

REGISTRY = "registry.ollama.ai"
MANIFEST_ACCEPT = "application/vnd.docker.distribution.manifest.v2+json"


# --------------------------------------------------------------------------- #
#  Parsing de l'entrée (URL ou "modele:tag")                                   #
# --------------------------------------------------------------------------- #
def parse_model_ref(ref: str, tag_override: str | None) -> tuple[str, str, str]:
    """Retourne (namespace, model, tag). Voir ollama_pull_manual.py."""
    namespace = "library"
    path = ref

    if ref.startswith("http://") or ref.startswith("https://"):
        parsed = urlparse(ref)
        parts = [p for p in parsed.path.split("/") if p]
        if not parts:
            sys.exit(f"URL invalide, impossible d'extraire le modèle : {ref}")
        if parts[0] == "library" and len(parts) >= 2:
            namespace = "library"
            path = parts[1]
        elif len(parts) >= 2:
            namespace = parts[0]
            path = parts[1]
        else:
            path = parts[0]
    else:
        if "/" in ref:
            namespace, path = ref.split("/", 1)

    if ":" in path:
        model, tag = path.split(":", 1)
    else:
        model, tag = path, "latest"

    if tag_override:
        tag = tag_override

    return namespace, model, tag


# --------------------------------------------------------------------------- #
#  Récupération du manifest                                                    #
# --------------------------------------------------------------------------- #
def fetch_manifest(namespace: str, model: str, tag: str) -> dict:
    url = f"https://{REGISTRY}/v2/{namespace}/{model}/manifests/{tag}"
    req = urllib.request.Request(url)
    req.add_header("Accept", MANIFEST_ACCEPT)
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(
                f"404 : modèle ou tag introuvable ({namespace}/{model}:{tag}).\n"
                f"Vérifie le nom et le tag sur https://ollama.com/library/{model}"
            )
        sys.exit(f"Erreur HTTP {e.code} sur le manifest : {e.reason}")
    except urllib.error.URLError as e:
        sys.exit(f"Impossible de joindre {REGISTRY} : {e.reason}")
    return json.loads(data)


# --------------------------------------------------------------------------- #
#  Affichage                                                                   #
# --------------------------------------------------------------------------- #
def human_size(n: int) -> str:
    for unit in ("o", "Ko", "Mo", "Go", "To"):
        if n < 1024:
            return f"{n:7.2f} {unit}"
        n /= 1024
    return f"{n:7.2f} Po"


def blob_url(namespace: str, model: str, digest: str) -> str:
    return f"https://{REGISTRY}/v2/{namespace}/{model}/blobs/{digest}"


def print_report(manifest: dict, namespace: str, model: str, tag: str) -> None:
    manifest_url = f"https://{REGISTRY}/v2/{namespace}/{model}/manifests/{tag}"

    print("=" * 78)
    print(f"  Modèle : {namespace}/{model}:{tag}")
    print("=" * 78)
    print(f"Manifest URL       : {manifest_url}")
    print(f"Schema version     : {manifest.get('schemaVersion')}")
    print(f"Manifest mediaType : {manifest.get('mediaType')}")
    print()

    blobs: list[tuple[str, str, int, str]] = []  # (role, mediaType, size, digest)

    config = manifest.get("config")
    if config:
        blobs.append(
            ("config", config.get("mediaType", ""), int(config.get("size", 0)),
             config["digest"])
        )

    for i, layer in enumerate(manifest.get("layers", []), 1):
        blobs.append(
            (f"layer {i}", layer.get("mediaType", ""), int(layer.get("size", 0)),
             layer["digest"])
        )

    total_size = sum(b[2] for b in blobs)

    print(f"Nombre de blobs    : {len(blobs)}")
    print(f"Taille totale      : {human_size(total_size)}  ({total_size} octets)")
    print()
    print("-" * 78)
    print("  Détail des blobs")
    print("-" * 78)

    for role, media_type, size, digest in blobs:
        algo, hexd = digest.split(":", 1)
        print()
        print(f"[{role}]")
        print(f"  mediaType  : {media_type}")
        print(f"  size       : {human_size(size)}  ({size} octets)")
        print(f"  digest     : {digest}")
        print(f"  blob file  : {algo}-{hexd}")
        print(f"  URL        : {blob_url(namespace, model, digest)}")

    print()
    print("-" * 78)
    print("  URLs brutes (pour curl / wget / téléchargement externe)")
    print("-" * 78)
    print(manifest_url)
    for _, _, _, digest in blobs:
        print(blob_url(namespace, model, digest))
    print()

    print("-" * 78)
    print("  Noms de fichiers bruts (arborescence Ollama locale)")
    print("-" * 78)
    print(f"manifests/{REGISTRY}/{namespace}/{model}/{tag}")
    for _, _, _, digest in blobs:
        algo, hexd = digest.split(":", 1)
        print(f"blobs/{algo}-{hexd}")
    print()


# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(
        description="Affiche les infos d'un modèle Ollama (URLs, SHA256, tailles) "
                    "sans rien télécharger d'autre que le manifest."
    )
    ap.add_argument("model", help="URL (…/library/<modele>[:tag]) ou 'modele[:tag]'")
    ap.add_argument("--tag", default=None, help="Tag explicite (prioritaire sur l'URL)")
    ap.add_argument("--json", action="store_true",
                    help="Affiche le manifest JSON brut au lieu du rapport formaté")
    args = ap.parse_args()

    namespace, model, tag = parse_model_ref(args.model, args.tag)
    manifest = fetch_manifest(namespace, model, tag)

    if args.json:
        print(json.dumps(manifest, indent=2))
        return

    print_report(manifest, namespace, model, tag)


if __name__ == "__main__":
    main()
