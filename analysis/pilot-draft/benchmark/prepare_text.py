#!/usr/bin/env python3
"""Turn each study's PDFs into one page-marked text file for the models.

    .venv/bin/python analysis/pilot-draft/benchmark/prepare_text.py [--study ID] [--force]

Every page goes through `pdftotext -layout`. A page whose text looks garbled
(too few words, too few dictionary words, or replacement characters) is sent as
an image to a pinned Gemini Flash model for transcription instead. Writes
data/interim/benchmark/text/<study_id>.txt and <study_id>.pages.json.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
RAW = REPO_ROOT / "data" / "raw" / "benchmark"
OUT = REPO_ROOT / "data" / "interim" / "benchmark" / "text"

OCR_MODEL = "gemini-3.7-flash"  # registered project default (DR-005); 3.8 Flash was overloaded (503) on 2026-09-22
MIN_TOKENS = 40          # fewer alphabetic tokens than this: treat as image-only
MIN_DICT_RATE = 0.70     # share of alphabetic tokens (3+ letters) found in the system dictionary
MAX_BAD_CHAR = 0.01      # share of replacement / control characters
OCR_PROMPT = (
    "Transcribe this page of a printed report exactly as written. Preserve the reading "
    "order, headings, footnotes and page numbers. Reproduce every table as rows of text with "
    "columns separated by ' | ', keeping every number, sign, asterisk and dagger exactly. "
    "Do not summarise, correct, or add anything. If the page is blank, return [blank page]."
)

WORDS = {w.strip().lower() for w in open("/usr/share/dict/words", encoding="utf-8")}


def garble_stats(text: str) -> dict:
    tokens = re.findall(r"[A-Za-z]{3,}", text)
    hits = sum(t.lower() in WORDS or t.lower().rstrip("s") in WORDS for t in tokens)
    bad = sum(c == "�" or (ord(c) < 32 and c not in "\n\t\f\r") for c in text)
    return {
        "n_tokens": len(tokens),
        "dict_rate": round(hits / max(len(tokens), 1), 3),
        "bad_char_rate": round(bad / max(len(text), 1), 4),
    }


def is_garbled(s: dict) -> bool:
    return s["n_tokens"] < MIN_TOKENS or s["dict_rate"] < MIN_DICT_RATE or s["bad_char_rate"] > MAX_BAD_CHAR


def page_texts(pdf: Path) -> list[str]:
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    pages = out.split("\f")
    return pages[:-1] if pages and not pages[-1].strip() else pages


def squeeze(text: str) -> str:
    lines = [l.rstrip() for l in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


OCR_CACHE = REPO_ROOT / "data" / "interim" / "benchmark" / "ocr"
# The direct Gemini API returned sustained 503s on 2026-09-22 and the SDK's own
# retries stalled each page for minutes; --ocr-direct re-enables it.
OCR_DIRECT = False


def ocr_page(client, pdf: Path, page_no: int) -> tuple[str, str]:
    """Transcribe one page image. Returns (text, route). Cached per page so reruns resume."""
    import base64
    import os

    import httpx
    from google.genai import types
    from tenacity import retry, stop_after_attempt, wait_exponential

    cache = OCR_CACHE / pdf.stem / f"p{page_no:04d}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return d["text"], d["route"]
    with tempfile.TemporaryDirectory() as tmp:
        stem = Path(tmp) / "p"
        subprocess.run(["pdftoppm", "-r", "150", "-png", "-f", str(page_no), "-l", str(page_no), "-singlefile", str(pdf), str(stem)], check=True)
        png = (Path(tmp) / "p.png").read_bytes()

    def direct():  # one attempt: when the direct API is overloaded it stays overloaded
        r = client.models.generate_content(
            model=OCR_MODEL,
            contents=[types.Part.from_bytes(data=png, mime_type="image/png"), OCR_PROMPT],
            config=types.GenerateContentConfig(temperature=0),
        )
        return r.text or ""

    @retry(stop=stop_after_attempt(6), wait=wait_exponential(min=5, max=90), reraise=True)
    def via_openrouter():
        b64 = base64.b64encode(png).decode()
        r = httpx.post("https://openrouter.ai/api/v1/chat/completions",
                       headers={"Authorization": f"Bearer {os.environ['OPEN_ROUTER_KEY']}"},
                       json={"model": f"google/{OCR_MODEL}", "temperature": 0, "messages": [{"role": "user", "content": [
                           {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                           {"type": "text", "text": OCR_PROMPT}]}]}, timeout=300)
        r.raise_for_status()
        d = r.json()
        if "error" in d:
            raise RuntimeError(d["error"])
        return d["choices"][0]["message"]["content"] or ""

    try:
        if not OCR_DIRECT:
            raise RuntimeError("direct route disabled")
        text, route = direct(), "gemini"
    except Exception:
        text, route = via_openrouter(), "openrouter"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"text": text, "route": route, "model": OCR_MODEL}), encoding="utf-8")
    return text, route


def prepare(study: dict, client_factory, force: bool) -> None:
    out_txt = OUT / f"{study['study_id']}.txt"
    if out_txt.exists() and not force:
        print(f"{study['study_id']}: exists, skipping")
        return
    pages_meta, jobs = [], []
    for stem in study["files"].split(";"):
        pdf = RAW / f"{stem}.pdf"
        for i, text in enumerate(page_texts(pdf), start=1):
            s = garble_stats(text)
            meta = {"file": stem, "page": i, **s, "source": "pdftotext", "text": squeeze(text)}
            if is_garbled(s):
                meta["source"] = "gemini_ocr"
                meta["ocr_model"] = OCR_MODEL
                jobs.append((meta, pdf, i))
            pages_meta.append(meta)
    if jobs:
        client = client_factory()
        with ThreadPoolExecutor(max_workers=8) as ex:
            for meta, (text, route) in zip([j[0] for j in jobs], ex.map(lambda j: ocr_page(client, j[1], j[2]), jobs)):
                meta["text"] = squeeze(text)
                meta["ocr_route"] = route
    body = "\n\n".join(f"===== FILE: {m['file']} | PAGE {m['page']} =====\n{m['text']}" for m in pages_meta)
    OUT.mkdir(parents=True, exist_ok=True)
    out_txt.write_text(body, encoding="utf-8")
    for m in pages_meta:
        m.pop("text")
    thresholds = {"min_tokens": MIN_TOKENS, "min_dict_rate": MIN_DICT_RATE, "max_bad_char": MAX_BAD_CHAR, "ocr_model": OCR_MODEL}
    (OUT / f"{study['study_id']}.pages.json").write_text(json.dumps({"thresholds": thresholds, "pages": pages_meta}, indent=1), encoding="utf-8")
    print(f"{study['study_id']}: {len(pages_meta)} pages, {len(jobs)} OCR, {len(body):,} chars (~{len(body)//4:,} tokens)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--ocr-direct", action="store_true", help="try the direct Gemini API before OpenRouter")
    args = ap.parse_args()
    global OCR_DIRECT
    OCR_DIRECT = args.ocr_direct

    def client_factory():
        from dotenv import load_dotenv
        from google import genai
        load_dotenv(REPO_ROOT / ".env")
        return genai.Client()

    with open(HERE / "manifest.csv", newline="", encoding="utf-8") as f:
        studies = [s for s in csv.DictReader(f) if not args.study or s["study_id"] == args.study]
    for s in studies:
        prepare(s, client_factory, args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
