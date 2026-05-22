import base64
import io
import sys
import time
from pathlib import Path
import requests
from pdf2image import convert_from_path
from PIL import Image


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "glm-ocr"
DEFAULT_PROMPT = (
    "Extract all text and tables from this document page as clean Markdown. "
    "Preserve table structure, column alignment and every numeric value "
    "(including currency symbols). Do not add commentary, do not summarize, "
    "transcribe every row without omission."
)

def image_to_b64(img, fmt: str = "PNG") -> str:
    """Encode une image PIL en base64 (sans préfixe data:)."""
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode()

def ocr_image(img_b64: str, model: str, prompt: str, timeout: int = 300) -> str:
    """Soumet une image encodée en base64 à GLM-OCR, renvoie le texte."""
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [img_b64],
        "stream": False,
        "options": {"temperature": 0},  # OCR déterministe
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json().get("response", "").strip()




def main():

    img_file = "corpus_tp/cptres1.jpg"
    img = Image.open(img_file)
    b = image_to_b64(img)
    md = ocr_image(b, DEFAULT_MODEL, DEFAULT_PROMPT)

    with open("output_2.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("[+] Résultat écrit dans output_2.md")
if __name__=='__main__':
    main()
