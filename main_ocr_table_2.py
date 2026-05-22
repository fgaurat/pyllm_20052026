import base64
import io
import sys
import time
from pathlib import Path
import requests
from pdf2image import convert_from_path


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



def process_pdf(pdf_file, model, max_tokens, prompt):
    pages = convert_from_path(str(pdf_file), dpi=300)
    # save intermediate images for debugging
    debug_dir = Path("debug_images")
    debug_dir.mkdir(exist_ok=True)
    for i, page in enumerate(pages, start=1):
        debug_path = debug_dir / f"page_{i}.png"
        page.save(debug_path)
        print(f"[+] Page {i} saved as {debug_path}", file=sys.stderr)
    # Further processing of pages can be added here
    print(f"[+] {len(pages)} page(s) détectée(s)", file=sys.stderr)
    sections = []
    for i, page in enumerate(pages, start=1):
        print(f"[+] Traitement de la page {i}...", file=sys.stderr)
        img_b64 = image_to_b64(page)
        text=""
        try:
            text = ocr_image(img_b64, model, prompt)
            print(f"[+] OCR de la page {i} terminé, {len(text)} caractères extraits", file=sys.stderr)
        except Exception as e:
            print(f"[-] Erreur lors de l'OCR de la page {i}: {e}", file=sys.stderr)
        sections.append(f"## Page {i}\n\n{text}")
        
    return "\n\n".join(sections)

def main():
    pdf_file = "corpus_tp/test_ocr_tables.pdf"
    md = process_pdf(pdf_file, DEFAULT_MODEL, 200, DEFAULT_PROMPT)

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("[+] Résultat écrit dans output.md")
if __name__=='__main__':
    main()
