#!/usr/bin/env python3
"""Run the extract_v1 prompt over one passage with Gemini structured output.

    python .claude/skills/gemini-extract/scripts/extract.py \
        --text-file data/interim/passages/frey-2019-technology-trap-p304.txt \
        --meta data/interim/passages/frey-2019-technology-trap-p304.meta.json

Writes one JSON file per run to `data/interim/extractions/` recording the model
snapshot actually used, the prompt version, and a hash of the input, so that any
record can be traced back to the exact call that drafted it.

Output is always a DRAFT. Nothing here writes to `data/processed/`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from models import ExtractionResult  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[4]
PROMPT_PATH = REPO_ROOT / "protocol" / "prompts" / "extract_v1.md"
PROMPT_VERSION = "extract_v1"
DEFAULT_MODEL = "gemini-3.7-flash"
DEFAULT_OUT = REPO_ROOT / "data" / "interim" / "extractions"


def load_system_prompt() -> str:
    """The registered prompt is the source of truth; never duplicate it in code."""
    text = PROMPT_PATH.read_text(encoding="utf-8")
    marker = "## System prompt"
    if marker not in text:
        raise SystemExit(f"{PROMPT_PATH} has no '{marker}' section")
    return text.split(marker, 1)[1].strip()


def relative_if_possible(path: Path) -> Path:
    """Record repo-relative paths; fall back to absolute for scratch files."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT)
    except ValueError:
        return resolved


def build_user_prompt(passage: str, meta: dict) -> str:
    meta_lines = "\n".join(f"- {k}: {v}" for k, v in meta.items())
    return (
        "SOURCE METADATA\n"
        f"{meta_lines}\n\n"
        "CANDIDATE PASSAGE (verbatim; do not correct OCR)\n"
        "-----\n"
        f"{passage}\n"
        "-----\n\n"
        "Extract the prediction record. If this passage contains no in-scope "
        "prediction about technology and human employment, set contains_prediction "
        "to false and explain why in reason_if_absent."
    )


def check_quote_grounded(result: ExtractionResult, passage: str) -> list[str]:
    """Cheap anti-hallucination check: the quote must occur in the input."""
    warnings: list[str] = []
    if result.record is None:
        return warnings
    quote = " ".join(result.record.quote_verbatim.split())
    haystack = " ".join(passage.split())
    if quote and quote not in haystack:
        warnings.append(
            "quote_verbatim is not a substring of the input passage — "
            "the model may have paraphrased or hallucinated it"
        )
    return warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--text-file", required=True, type=Path)
    ap.add_argument("--meta", type=Path, help="JSON file of source metadata")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Build the prompt and schema, print them, make no API call",
    )
    args = ap.parse_args()

    passage = args.text_file.read_text(encoding="utf-8")
    meta = json.loads(args.meta.read_text(encoding="utf-8")) if args.meta else {}
    system_prompt = load_system_prompt()
    user_prompt = build_user_prompt(passage, meta)

    if args.dry_run:
        print(f"system prompt: {len(system_prompt)} chars from {PROMPT_PATH}")
        print(f"user prompt:   {len(user_prompt)} chars")
        print(f"model:         {args.model}")
        print(
            "schema fields: "
            + ", ".join(ExtractionResult.model_json_schema()["properties"])
        )
        return 0

    from dotenv import load_dotenv
    from google import genai
    from google.genai import types

    load_dotenv(REPO_ROOT / ".env")
    client = genai.Client()

    response = client.models.generate_content(
        model=args.model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0,
            response_mime_type="application/json",
            response_schema=ExtractionResult,
        ),
    )

    result = ExtractionResult.model_validate_json(response.text)
    warnings = check_quote_grounded(result, passage)

    payload = {
        "model_requested": args.model,
        "model_version": getattr(response, "model_version", None),
        "prompt_version": PROMPT_VERSION,
        "input_file": str(relative_if_possible(args.text_file)),
        "input_sha256": hashlib.sha256(passage.encode("utf-8")).hexdigest(),
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_meta": meta,
        "warnings": warnings,
        "result": result.model_dump(),
    }

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = args.out / f"{args.text_file.stem}-{stamp}.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), "utf-8")

    print(f"wrote {out_path}")
    print(f"model_version: {payload['model_version']}")
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
