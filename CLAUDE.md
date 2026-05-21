# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is a **3-day training course** (in French) on designing a RAG (Retrieval-Augmented Generation) system for actuarial data. The repo bundles:

- Course materials: `slides-j1.md`, `slides-j2.md`, `slides-j3.md`, `Conception d'un système RAG pour l'exploitation de données actuarielles.md`, `glossaire-llm.md`
- A practice corpus in `corpus_tp/` (PDFs, .docx, .xlsx, .md files about houseplants — used as ingestion material for RAG exercises)
- Standalone Python demo scripts (one feature per file, not a coherent application)

There is no application architecture to preserve — each `main_*.py` is an independent demo for a specific lesson.

## Toolchain

- Python ≥ 3.8 (pinned to `3.8` in `.python-version`)
- Dependency manager: **uv** (lockfile is `uv.lock`, not `requirements.txt`)
- Local LLM runtime: **Ollama** (scripts target `http://localhost:11434` with the `mistral` model)
- Browser automation: **Playwright** (Chromium)

## Common commands

```bash
# Install / sync dependencies (uv reads pyproject.toml + uv.lock)
uv sync

# Run a demo script
uv run python main_hello_ollama.py
uv run python main_boursorama.py
uv run python main_boursorama_pw.py

# One-off: install Playwright browsers after `uv sync`
uv run playwright install chromium

# Ollama must be running locally before Ollama-backed scripts work
ollama serve            # in another terminal
ollama pull mistral     # first time only
```

There are no tests, no linter config, and no build step — do not invent them.

## Demo scripts at a glance

- `main.py` — placeholder hello-world from `uv init`.
- `main_hello_ollama.py` — minimal Ollama chat call using the `ollama` Python client; `oldmain()` is kept as a reference for the raw `POST /v1/chat/completions` HTTP form.
- `main_boursorama.py` — `requests` + BeautifulSoup scraping of Boursorama's search AJAX endpoint by ISIN code; writes `tf1.html` as a debug artifact.
- `main_boursorama_pw.py` — Playwright equivalent (headed Chromium) that screenshots the homepage to `screenshot.png`. Use this when the `requests` version gets blocked.

When adding more demos, follow the same pattern: a single `main_<topic>.py` file with a `main()` function and an `if __name__ == '__main__'` guard. Do not refactor existing scripts into a shared package — the per-file isolation is intentional for teaching.

## Working with the course content

- The `slides-*.md` and glossary files are the deliverable. Edits to them are the most common task.
- The corpus in `corpus_tp/` is intentionally heterogeneous (scanned PDFs, formatted PDFs, .docx, .xlsx, .md) so trainees practice multi-format ingestion — don't "clean it up" or normalize formats.
- Course language is French; keep new prose, comments, and slide content in French unless the user writes in English.
