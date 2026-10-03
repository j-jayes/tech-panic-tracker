#!/usr/bin/env python3
"""Two-pass extraction (extract + adversarial self-review) for each study x model.

    .venv/bin/python analysis/pilot-draft/benchmark/run_extraction.py --dry-run
    .venv/bin/python analysis/pilot-draft/benchmark/run_extraction.py --study jtpa --models gemini-3.8-flash
    .venv/bin/python analysis/pilot-draft/benchmark/run_extraction.py --budget-usd 40
    .venv/bin/python analysis/pilot-draft/benchmark/run_extraction.py --jev

Writes data/interim/benchmark/runs/<study>/<model>/pass{1,2}.json. Existing
outputs are skipped unless --force. Models run in parallel, studies in sequence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from providers import (  # noqa: E402
    PRICES, Budget, BudgetExceeded, GeminiClient, JevClient, OpenRouterClient,
    call_result_record, estimate_cost, log_call,
)
from pydantic import ValidationError  # noqa: E402
from schema import ExtractionOutput, ReviewOutput  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PROMPTS = REPO_ROOT / "protocol" / "prompts"
TEXT = REPO_ROOT / "data" / "interim" / "benchmark" / "text"
RUNS = REPO_ROOT / "data" / "interim" / "benchmark" / "runs"

MODELS = {  # short key -> (client, exact model id)
    "gemini-3.8-flash": ("gemini", "gemini-3.8-flash"),
    "gemini-3.1-pro": ("gemini", "gemini-3.1-pro-preview"),
    "claude-opus-5": ("openrouter", "anthropic/claude-opus-5"),
    "gpt-5.6-terra": ("openrouter", "openai/gpt-5.6-terra"),
    "deepseek-v4.1-flash": ("openrouter", "deepseek/deepseek-v4.1-flash"),
}
CONTEXT_TOKENS = 1_000_000  # all five models advertise >= 1M tokens
JEV_EXCERPT_CHARS = 60_000   # Jev's window is 32k tokens

_lock = threading.Lock()
_gemini_down: set[str] = set()
NO_FALLBACK = False  # --no-fallback: keep Gemini on the direct API (e.g. when OpenRouter credit is exhausted)  # models whose direct Gemini route has failed with 503 this run


def load_system_prompt(name: str) -> str:
    text = (PROMPTS / f"{name}.md").read_text(encoding="utf-8")
    marker = "## System prompt"
    if marker not in text:
        raise SystemExit(f"{name}.md has no '{marker}' section")
    return text.split(marker, 1)[1].strip()


def studies(only: str | None) -> list[dict]:
    with open(HERE / "manifest.csv", newline="", encoding="utf-8") as f:
        return [s for s in csv.DictReader(f) if not only or s["study_id"] in only.split(",")]


# Both passes send the same system message and the same source block first, so the
# provider can serve pass 2's long prefix from its prompt cache (automatic for OpenAI,
# DeepSeek and Gemini). The registered pass-specific instructions follow the document,
# which is also where long-context guidance recommends placing the task.
SYSTEM_SHARED = (
    "You are a careful research assistant extracting data from reports of randomized "
    "evaluations of US job-training programs, for a meta-analysis. The source text comes "
    "first; the task instructions follow it. Follow the task instructions exactly."
)


def source_block(study: dict, text: str) -> str:
    return f"STUDY: {study['project']}\nFILES: {', '.join(study['files'].split(';'))}\n\nSOURCE TEXT\n{text}\nEND OF SOURCE TEXT\n"


def pass1_user(study: dict, text: str, instructions: str) -> str:
    return source_block(study, text) + "\nTASK INSTRUCTIONS\n" + instructions + "\n\nExtract one record per pre-randomization experiment unit."


def pass2_user(study: dict, text: str, instructions: str, draft: dict) -> str:
    return (
        source_block(study, text)
        + "\nTASK INSTRUCTIONS\n" + instructions
        + "\n\nDRAFT EXTRACTION TO REVIEW (JSON)\n"
        + json.dumps(draft, indent=1, ensure_ascii=False)
        + "\n\nReview the draft against the source text and return the corrected records and the change log."
    )


def rel(p: Path) -> str:
    return str(p.resolve().relative_to(REPO_ROOT))


def run_pass(client, model_key: str, model_id: str, study: dict, n: int, system: str, user: str,
             schema, prompt_version: str, text_path: Path, text: str, budget: Budget, force: bool) -> dict | None:
    out = RUNS / study["study_id"] / model_key / f"pass{n}.json"
    if out.exists() and not force:
        return json.loads(out.read_text())
    est = estimate_cost(model_id, (len(system) + len(user)) // 4)
    if client.api == "openrouter":
        with _lock:
            budget.check(est)
    base = {"study_id": study["study_id"], "model_key": model_key, "model_requested": model_id, "pass": n, "api": client.api}
    try:
        try:
            if model_id in _gemini_down:
                raise RuntimeError("503 (direct route marked down earlier in this run)")
            try:
                res = client.complete(model_id, system, user, schema)
            except ValidationError as exc:  # malformed or empty reply: one retry, logged
                log_call(**base, status="error", error=f"ValidationError (retrying once): {exc}"[:2000])
                res = client.complete(model_id, system, user, schema)
            route = client.api
        except Exception as exc:
            # Gemini direct can stay overloaded (503) for hours; the same model is then
            # reached through OpenRouter's Google route. The route is recorded per run.
            if client.api != "gemini" or "503" not in str(exc) or NO_FALLBACK:
                raise
            print(f"  {study['study_id']} {model_key} pass{n}: Gemini direct 503, falling back to OpenRouter", flush=True)
            if model_id not in _gemini_down:
                log_call(**base, status="error", error=f"{type(exc).__name__}: {exc}"[:2000])
            _gemini_down.add(model_id)
            with _lock:
                budget.check(est)
            res = OpenRouterClient().complete(f"google/{model_id}", system, user, schema)
            route = "openrouter"
            base = {**base, "api": "openrouter"}
    except BudgetExceeded:
        raise
    except Exception as exc:  # recorded, not fatal: the report shows failures as gaps
        log_call(**base, status="error", error=f"{type(exc).__name__}: {exc}"[:2000])
        print(f"  ERROR {study['study_id']} {model_key} pass{n}: {type(exc).__name__}: {str(exc)[:300]}", flush=True)
        return None
    rec = call_result_record(res)
    with _lock:
        if route == "openrouter":
            budget.add(res.cost_usd)
    log_call(**base, status="ok", **{k: rec[k] for k in ("model_version", "provider", "input_tokens", "output_tokens", "reasoning_tokens", "cost_usd", "latency_s", "structured_mode")})
    payload = {
        "model_requested": model_id,
        "model_version": res.model_version,
        "provider": res.provider,
        "route": route,
        "prompt_version": prompt_version,
        "pass": n,
        "study_id": study["study_id"],
        "project": study["project"],
        "input_file": rel(text_path),
        "input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "params": res.params,
        "structured_mode": res.structured_mode,
        "usage": {k: rec[k] for k in ("input_tokens", "output_tokens", "reasoning_tokens", "cost_usd", "latency_s")},
        "warnings": res.warnings,
        "result": res.parsed.model_dump(),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    cost = f"${res.cost_usd:.3f}" if res.cost_usd is not None else "$?"
    print(f"  {study['study_id']:12s} {model_key:20s} pass{n}: {len(res.parsed.records)} records, "
          f"{res.input_tokens:,} in / {res.output_tokens:,} out, {cost}, {res.latency_s:.0f}s", flush=True)
    return payload


def run_model(model_key: str, sts: list[dict], budget: Budget, force: bool, passes: set[int]) -> None:
    api, model_id = MODELS[model_key]
    client = GeminiClient() if api == "gemini" else OpenRouterClient()
    sys1 = load_system_prompt("benchmark_extract_v1")
    sys2 = load_system_prompt("benchmark_review_v1").replace("{EXTRACT_PROMPT}", sys1)
    for s in sts:
        text_path = TEXT / f"{s['study_id']}.txt"
        text = text_path.read_text(encoding="utf-8")
        try:
            p1 = run_pass(client, model_key, model_id, s, 1, SYSTEM_SHARED, pass1_user(s, text, sys1), ExtractionOutput,
                          "benchmark_extract_v1", text_path, text, budget, force) if 1 in passes else None
            if 2 in passes:
                if p1 is None:
                    p1_path = RUNS / s["study_id"] / model_key / "pass1.json"
                    p1 = json.loads(p1_path.read_text()) if p1_path.exists() else None
                if p1 is not None:
                    run_pass(client, model_key, model_id, s, 2, SYSTEM_SHARED, pass2_user(s, text, sys2, p1["result"]), ReviewOutput,
                             "benchmark_review_v1", text_path, text, budget, force)
        except BudgetExceeded as exc:
            print(f"  BUDGET STOP {model_key}: {exc}", flush=True)
            return


# --- Jev -----------------------------------------------------------------

YES_NO = {"yes": "the statement is true of this intervention", "no": "the statement is not true of this intervention"}
JEV_QUESTIONS = {
    "training_role": ("Role of training in the intervention delivered to this experiment unit.",
                      {"primary": "training or classroom instruction is the core service",
                       "secondary": "training is one service among others, ancillary to the core service",
                       "incidental": "training is a minor or occasional element"}),
    "has_classroom": ("The intervention includes formal classroom instruction: vocational, GED, basic education, ESL, or college.", YES_NO),
    "has_ojt": ("The intervention includes on-the-job training, apprenticeships, or structured work experience.", YES_NO),
    "has_jsa": ("The intervention includes job search assistance, job clubs, counseling, or placement services.", YES_NO),
    "has_multiple_components": ("The intervention bundles more than one of classroom training, on-the-job training and job search assistance, or includes other substantial components.", YES_NO),
    "mandatory_voluntary": ("Was participation mandatory (e.g. a condition of receiving welfare) or voluntary?",
                            {"mandatory": "participation was required", "voluntary": "participation was voluntary"}),
    "funding_public_private": ("Who funds the administration of the evaluated program (operational funding, not the evaluation)?",
                               {"public": "government appropriations are the dominant funding source",
                                "private": "philanthropic, corporate, or nonprofit self-generated funds are the dominant source",
                                "mixed": "significant contributions from both public and private sectors"}),
    "admin_public_private": ("Who administers the program day-to-day?",
                             {"public": "government agency such as a welfare office, workforce board, or public community college",
                              "private": "nonprofit organization, community-based organization, or for-profit company",
                              "mixed": "formal public-private partnership, or government program that contracts out core service delivery"}),
    "sector_program": ("This is a sector program: sector-focused training by a community-based organization with employer engagement, targeting a specific industry, with employers involved in designing the curriculum.", YES_NO),
}


def run_jev(sts: list[dict], gold_units: dict, budget: Budget, force: bool) -> None:
    client = JevClient()
    questions = {k: {"type": "choice", "instructions": ins, "criteria": crit} for k, (ins, crit) in JEV_QUESTIONS.items()}
    for s in sts:
        out = RUNS / s["study_id"] / "jev-1.13" / "answers.json"
        if out.exists() and not force:
            continue
        text = (TEXT / f"{s['study_id']}.txt").read_text(encoding="utf-8")
        excerpt = text[:JEV_EXCERPT_CHARS]
        rows = []
        for unit in gold_units[s["project"]]:
            state = f"STUDY: {s['project']}\nEXPERIMENT UNIT TO CLASSIFY: {unit}\nREPORT EXCERPT:\n{excerpt}"
            budget.check(0.01)
            try:
                d = client.ask(state, questions)
            except Exception as exc:
                log_call(study_id=s["study_id"], model_key="jev-1.13", model_requested=client.model, pass_=1, api="openrouter", status="error", error=str(exc)[:2000])
                print(f"  ERROR jev {s['study_id']} {unit}: {exc}")
                continue
            u = d.get("usage", {})
            budget.add(u.get("cost"))
            log_call(study_id=s["study_id"], model_key="jev-1.13", model_requested=client.model, pass_=1, api="openrouter", status="ok",
                     model_version=d.get("model"), provider=d.get("provider"), input_tokens=u.get("input_tokens"), output_tokens=u.get("output_tokens"),
                     reasoning_tokens=0, cost_usd=u.get("cost"), latency_s=None, structured_mode="decisions")
            rows.append({"site_subgroup": unit, "model_version": d.get("model"), "answers": d.get("answers"), "usage": u})
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "model_requested": client.model, "prompt_version": "benchmark_jev_v1", "study_id": s["study_id"],
            "excerpt_chars": len(excerpt), "excerpt_sha256": hashlib.sha256(excerpt.encode()).hexdigest(),
            "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "questions": questions, "units": rows,
        }, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"  jev {s['study_id']}: {len(rows)} units")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--study", help="comma-separated study ids")
    ap.add_argument("--models", help="comma-separated model keys", default=",".join(MODELS))
    ap.add_argument("--pass", dest="passes", default="1,2")
    ap.add_argument("--budget-usd", type=float, default=47.0)  # key cap is $50
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--jev", action="store_true", help="run the Jev classification entrant instead")
    ap.add_argument("--no-fallback", action="store_true", help="never route Gemini models through OpenRouter")
    args = ap.parse_args()
    global NO_FALLBACK
    NO_FALLBACK = args.no_fallback

    # Shortest reports first, so a budget stop truncates the longest studies rather than a random subset.
    sts = sorted(studies(args.study), key=lambda s: (TEXT / f"{s['study_id']}.txt").stat().st_size)
    keys = args.models.split(",")
    budget = Budget(args.budget_usd)
    print(f"OpenRouter spend: ${budget.spent:.2f}; effective limit ${budget.limit:.2f} (key limit or account credit, whichever is lower)")

    if args.dry_run:
        sys1 = load_system_prompt("benchmark_extract_v1")
        sys2 = load_system_prompt("benchmark_review_v1").replace("{EXTRACT_PROMPT}", sys1)
        print(f"system prompts: pass1 {len(sys1):,} chars, pass2 {len(sys2):,} chars")
        total = {k: 0.0 for k in keys}
        for s in sts:
            n = len((TEXT / f"{s['study_id']}.txt").read_text(encoding="utf-8"))
            tok = n // 4
            flag = "  OVER CONTEXT" if tok > CONTEXT_TOKENS * 0.9 else ""
            print(f"{s['study_id']:12s} {n:>10,} chars ~{tok:>9,} tokens{flag}")
            for k in keys:
                total[k] += estimate_cost(MODELS[k][1], tok) + estimate_cost(MODELS[k][1], tok + 8_000)
        for k in keys:
            print(f"projected two-pass cost {k:20s} ${total[k]:6.2f}")
        return 0

    if args.jev:
        import pandas as pd
        g = pd.read_excel(REPO_ROOT / "data" / "raw" / "roodman-massenkoff-2026-extraction-full-v69.xlsx", sheet_name="Data Table")
        gold_units = {p: g.loc[g.project == p, "site_subgroup"].tolist() for p in g.project.dropna().unique()}
        run_jev(sts, gold_units, budget, args.force)
        return 0

    passes = {int(p) for p in args.passes.split(",")}
    with ThreadPoolExecutor(max_workers=len(keys)) as ex:
        futs = [ex.submit(run_model, k, sts, budget, args.force, passes) for k in keys]
        for f in futs:
            try:
                f.result()
            except Exception:
                traceback.print_exc()
    print(f"OpenRouter spend now logged: ${budget.spent:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
