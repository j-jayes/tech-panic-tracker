#!/usr/bin/env python3
"""Download the benchmark's source reports and the gold workbook into data/raw/.

    .venv/bin/python analysis/pilot-draft/benchmark/fetch_sources.py          # fetch missing files
    .venv/bin/python analysis/pilot-draft/benchmark/fetch_sources.py --check  # print sha256 and page counts

data/raw/ is git-ignored; manifest.csv records where each file came from.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
RAW = REPO_ROOT / "data" / "raw" / "benchmark"
GOLD_URL = "https://raw.githubusercontent.com/droodman/job-training-meta-analysis/main/data/extraction_full_v69.xlsx"
GOLD_PATH = REPO_ROOT / "data" / "raw" / "roodman-massenkoff-2026-extraction-full-v69.xlsx"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"


def manifest() -> list[dict]:
    with open(HERE / "manifest.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pages(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    return int(next(l.split()[-1] for l in out.splitlines() if l.startswith("Pages")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    targets = [(GOLD_PATH, GOLD_URL)]
    for s in manifest():
        targets += [(RAW / f"{stem}.pdf", url) for stem, url in zip(s["files"].split(";"), s["urls"].split(";"))]
    for path, url in targets:
        if not path.exists() and not args.check:
            r = httpx.get(url, headers={"User-Agent": UA}, follow_redirects=True, timeout=180)
            r.raise_for_status()
            path.write_bytes(r.content)
        if path.exists():
            sha = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
            n = pages(path) if path.suffix == ".pdf" else ""
            print(f"{path.name:62s} {sha} {n}")
        else:
            print(f"{path.name:62s} MISSING ({url})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
