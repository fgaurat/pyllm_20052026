#!/usr/bin/env python3
"""
ollama_pull_manual.py
=====================

Télécharge un modèle Ollama "à la main" depuis le registre OCI
(registry.ollama.ai) et reconstitue l'arborescence locale attendue
par Ollama, sans passer par `ollama pull`.

Utile pour contourner un filtrage réseau (ex: Fortinet) qui bloque
le client Ollama mais laisse passer le HTTPS standard, ou pour
pré-télécharger sur une machine hors réseau filtré puis transférer.

Usage
-----
    # URL de la page modèle (tag déduit, "latest" par défaut)
    python ollama_pull_manual.py https://www.ollama.com/library/mistral-small3.2 ./ollama-models

    # Tag dans l'URL
    python ollama_pull_manual.py https://www.ollama.com/library/mistral-small3.2:24b ./ollama-models

    # Ou format court "modele:tag"
    python ollama_pull_manual.py mistral-small3.2:24b ./ollama-models

    # Tag explicite en option (prioritaire sur celui de l'URL)
    python ollama_pull_manual.py mistral-small3.2 ./ollama-models --tag 24b

Arborescence produite (dans <dest>)
-----------------------------------
    blobs/
        sha256-<digest>          # config + chaque layer (note: tiret, pas ':')
    manifests/
        registry.ollama.ai/library/<modele>/<tag>   # le manifest JSON

Si <dest> est ta racine ~/.ollama/models, Ollama voit le modèle
immédiatement (ollama list / ollama run). Sinon, copie blobs/ et
manifests/ vers cette racine sur la machine cible.

Dépendances : uniquement la lib standard (urllib). Aucune install.
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

REGISTRY = "registry.ollama.ai"
# Header obligatoire : le registre OCI répond en manifest v2
MANIFEST_ACCEPT = "application/vnd.docker.distribution.manifest.v2+json"
CHUNK = 1024 * 1024  # 1 Mo


# --------------------------------------------------------------------------- #
#  Parsing de l'entrée (URL ou "modele:tag")                                   #
# --------------------------------------------------------------------------- #
def parse_model_ref(ref: str, tag_override: str | None) -> tuple[str, str, str]:
    """
    Retourne (namespace, model, tag).

    Accepte :
      - https://www.ollama.com/library/mistral-small3.2
      - https://ollama.com/library/mistral-small3.2:24b
      - https://www.ollama.com/library/user/mymodel:tag  (namespace custom)
      - mistral-small3.2
      - mistral-small3.2:24b
      - user/mymodel:tag
    """
    namespace = "library"
    path = ref

    if ref.startswith("http://") or ref.startswith("https://"):
        parsed = urlparse(ref)
        # /library/mistral-small3.2  ->  ['library', 'mistral-small3.2']
        parts = [p for p in parsed.path.split("/") if p]
        if not parts:
            sys.exit(f"URL invalide, impossible d'extraire le modèle : {ref}")
        if parts[0] == "library" and len(parts) >= 2:
            namespace = "library"
            path = parts[1]
        elif len(parts) >= 2:
            # namespace custom : /<user>/<model>
            namespace = parts[0]
            path = parts[1]
        else:
            path = parts[0]
    else:
        # format court éventuellement "user/model:tag"
        if "/" in ref:
            namespace, path = ref.split("/", 1)

    # tag éventuel collé au nom
    if ":" in path:
        model, tag = path.split(":", 1)
    else:
        model, tag = path, "latest"

    if tag_override:
        tag = tag_override

    return namespace, model, tag


# --------------------------------------------------------------------------- #
#  HTTP helpers                                                                #
# --------------------------------------------------------------------------- #
def _request(url: str, accept: str | None = None) -> urllib.request.Request:
    req = urllib.request.Request(url)
    if accept:
        req.add_header("Accept", accept)
    return req


def fetch_manifest(namespace: str, model: str, tag: str) -> dict:
    url = f"https://{REGISTRY}/v2/{namespace}/{model}/manifests/{tag}"
    print(f"→ Manifest : {url}")
    try:
        with urllib.request.urlopen(_request(url, MANIFEST_ACCEPT)) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(
                f"404 : modèle ou tag introuvable ({namespace}/{model}:{tag}).\n"
                f"Vérifie le nom et le tag sur https://ollama.com/library/{model}"
            )
        sys.exit(f"Erreur HTTP {e.code} sur le manifest : {e.reason}")
    except urllib.error.URLError as e:
        sys.exit(
            f"Impossible de joindre {REGISTRY} : {e.reason}\n"
            f"(réseau filtré ? lance le script sur une machine avec accès libre)"
        )
    return json.loads(data)


def download_blob(namespace: str, model: str, digest: str, dest_blobs: Path) -> None:
    """
    Télécharge un blob et l'écrit sous blobs/sha256-<hex>.
    Skip si déjà présent et SHA correct. Vérifie le SHA après écriture.
    """
    algo, hexdigest = digest.split(":", 1)  # 'sha256', 'abcd...'
    filename = f"{algo}-{hexdigest}"        # nom sur disque : tiret, pas ':'
    target = dest_blobs / filename

    if target.exists():
        # vérif rapide : on revérifie le hash pour être sûr (air-gap = confiance)
        if _sha256_of(target) == hexdigest:
            print(f"  ✓ {filename[:19]}… déjà présent (SHA ok), skip")
            return
        print(f"  ⚠ {filename[:19]}… présent mais SHA incorrect, retéléchargement")

    url = f"https://{REGISTRY}/v2/{namespace}/{model}/blobs/{digest}"
    print(f"  → {url}")
    tmp = target.with_suffix(".part")
    h = hashlib.sha256()
    downloaded = 0

    try:
        with urllib.request.urlopen(_request(url)) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            with open(tmp, "wb") as f:
                while True:
                    block = resp.read(CHUNK)
                    if not block:
                        break
                    f.write(block)
                    h.update(block)
                    downloaded += len(block)
                    _progress(filename, downloaded, total)
        print()  # newline après la barre
    except urllib.error.URLError as e:
        tmp.unlink(missing_ok=True)
        sys.exit(f"Erreur de téléchargement du blob {filename[:19]}… : {e}")

    # Contrôle d'intégrité
    if h.hexdigest() != hexdigest:
        tmp.unlink(missing_ok=True)
        sys.exit(
            f"SHA256 NON conforme pour {filename} !\n"
            f"  attendu : {hexdigest}\n  obtenu  : {h.hexdigest()}"
        )
    tmp.rename(target)


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def _progress(name: str, done: int, total: int) -> None:
    short = name[:19] + "…"
    if total:
        pct = done / total * 100
        mb = done / 1_048_576
        tmb = total / 1_048_576
        sys.stdout.write(f"\r  ↓ {short} {pct:5.1f}%  ({mb:7.1f}/{tmb:.1f} Mo)")
    else:
        mb = done / 1_048_576
        sys.stdout.write(f"\r  ↓ {short} {mb:7.1f} Mo")
    sys.stdout.flush()


# --------------------------------------------------------------------------- #
#  Écriture du manifest sur disque                                             #
# --------------------------------------------------------------------------- #
def write_manifest(manifest: dict, namespace: str, model: str, tag: str,
                   dest: Path) -> None:
    manifest_dir = dest / "manifests" / REGISTRY / namespace / model
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / tag
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f)
    print(f"→ Manifest écrit : {manifest_path}")


# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(
        description="Télécharge un modèle Ollama à la main (registre OCI)."
    )
    ap.add_argument("model", help="URL (…/library/<modele>[:tag]) ou 'modele[:tag]'")
    ap.add_argument("dest", help="Dossier de destination (racine ~/.ollama/models ou neutre)")
    ap.add_argument("--tag", default=None, help="Tag explicite (prioritaire sur l'URL)")
    args = ap.parse_args()

    namespace, model, tag = parse_model_ref(args.model, args.tag)
    dest = Path(args.dest).expanduser().resolve()

    print(f"Modèle    : {namespace}/{model}:{tag}")
    print(f"Destination : {dest}\n")

    blobs_dir = dest / "blobs"
    blobs_dir.mkdir(parents=True, exist_ok=True)

    manifest = fetch_manifest(namespace, model, tag)

    # Liste des blobs à récupérer : le config + tous les layers
    digests: list[str] = []
    config_digest = manifest.get("config", {}).get("digest")
    if config_digest:
        digests.append(config_digest)
    for layer in manifest.get("layers", []):
        digests.append(layer["digest"])

    if not digests:
        sys.exit("Manifest sans config ni layers — format inattendu.")

    print(f"\n{len(digests)} blob(s) à récupérer :\n")
    for i, digest in enumerate(digests, 1):
        print(f"[{i}/{len(digests)}]")
        download_blob(namespace, model, digest, blobs_dir)

    write_manifest(manifest, namespace, model, tag, dest)

    print("\n✓ Terminé.")
    if dest.name == "models" and dest.parent.name == ".ollama":
        print("  Ollama devrait voir le modèle directement : ollama list")
    else:
        print("  Pour activer le modèle, copie les dossiers vers la racine Ollama :")
        print(f"    cp -r {dest}/blobs {dest}/manifests ~/.ollama/models/")
    print(f"  Puis : ollama run {model}:{tag}")


if __name__ == "__main__":
    main()