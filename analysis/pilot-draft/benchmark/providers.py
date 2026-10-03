"""Model clients for the extraction benchmark: Gemini (direct), OpenRouter (chat), Jev (decisions).

Each generative client exposes complete(model, system, user, schema) -> CallResult.
Every call is appended to data/interim/benchmark/calls.jsonl; Budget refuses a call
that would take OpenRouter spend past the limit, counting spend already logged.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx
from pydantic import BaseModel
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from schema import strict_json_schema

REPO_ROOT = Path(__file__).resolve().parents[3]
CALL_LOG = REPO_ROOT / "data" / "interim" / "benchmark" / "calls.jsonl"
OPENROUTER = "https://openrouter.ai/api"

# USD per million tokens (input, output), list prices checked 2026-09-22 on
# openrouter.ai/api/v1/models. OpenRouter calls log the billed cost it returns;
# these are used only for Gemini-direct calls and for pre-flight estimates.
PRICES = {
    "gemini-3.8-flash": (0.75, 3.75),
    "google/gemini-3.8-flash": (0.75, 3.75),
    "google/gemini-3.1-pro-preview": (2.00, 12.00),
    "gemini-3.1-pro-preview": (2.00, 12.00),
    "anthropic/claude-opus-5": (5.00, 25.00),
    "openai/gpt-5.6-terra": (2.00, 12.00),
    "deepseek/deepseek-v4.1-flash": (0.15, 0.60),
    "typesafe/jev-1.13": (0.042, 0.0),
}


@dataclass
class CallResult:
    text: str
    parsed: BaseModel | None
    model_version: str | None
    provider: str | None
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float | None = None
    latency_s: float = 0.0
    structured_mode: str = ""
    params: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    """Caps OpenRouter spend; Gemini runs on a separate billed key and is logged but not capped."""

    def __init__(self, limit_usd: float):
        self.limit = limit_usd
        logged = 0.0
        if CALL_LOG.exists():
            for line in CALL_LOG.read_text().splitlines():
                rec = json.loads(line)
                if rec.get("api") == "openrouter" and rec.get("cost_usd"):
                    logged += rec["cost_usd"]
        # The key's own billed usage also counts OCR calls made by prepare_text.py.
        self.spent = max(logged, openrouter_key_usage())
        # The account's credit balance can be lower than the key limit (other keys share it).
        remaining = openrouter_account_remaining()
        if remaining is not None:
            self.limit = min(self.limit, self.spent + remaining - 0.25)

    def check(self, estimate: float) -> None:
        if self.spent + estimate > self.limit:
            raise BudgetExceeded(f"spent ${self.spent:.2f} + estimate ${estimate:.2f} > limit ${self.limit:.2f}")

    def add(self, cost: float | None) -> None:
        self.spent += cost or 0.0


def openrouter_key_usage() -> float:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
    try:
        r = httpx.get(f"{OPENROUTER}/v1/auth/key", headers={"Authorization": f"Bearer {os.environ['OPEN_ROUTER_KEY']}"}, timeout=30)
        return float(r.json()["data"]["usage"])
    except Exception:
        return 0.0


def openrouter_account_remaining() -> float | None:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
    try:
        r = httpx.get(f"{OPENROUTER}/v1/credits", headers={"Authorization": f"Bearer {os.environ['OPEN_ROUTER_KEY']}"}, timeout=30)
        d = r.json()["data"]
        return float(d["total_credits"]) - float(d["total_usage"])
    except Exception:
        return None


def log_call(**rec) -> None:
    CALL_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec["run_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(CALL_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def estimate_cost(model: str, input_tokens: int, output_tokens: int = 30_000) -> float:
    pin, pout = PRICES[model]
    return (input_tokens * pin + output_tokens * pout) / 1e6


def _transient(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (408, 429, 500, 502, 503, 504, 529)
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    return type(exc).__name__ in ("ServerError",) or "503" in str(exc) or "429" in str(exc)


retrying = retry(retry=retry_if_exception(_transient), stop=stop_after_attempt(6), wait=wait_exponential(min=10, max=120), reraise=True)
retrying_patient = retry(retry=retry_if_exception(_transient), stop=stop_after_attempt(12), wait=wait_exponential(min=30, max=300), reraise=True)


class GeminiClient:
    api = "gemini"

    def __init__(self):
        from dotenv import load_dotenv
        from google import genai

        load_dotenv(REPO_ROOT / ".env")
        self.client = genai.Client()

    @retrying_patient
    def complete(self, model: str, system: str, user: str, schema: type[BaseModel]) -> CallResult:
        from google.genai import types

        t0 = time.time()
        r = self.client.models.generate_content(
            model=model,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0,
                max_output_tokens=65_536,
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        u = r.usage_metadata
        tin, tout, tthink = u.prompt_token_count or 0, u.candidates_token_count or 0, u.thoughts_token_count or 0
        pin, pout = PRICES[model]
        text = r.text or ""
        return CallResult(
            text=text,
            parsed=schema.model_validate_json(text),
            model_version=r.model_version,
            provider="Google AI Studio",
            input_tokens=tin,
            output_tokens=tout + tthink,
            reasoning_tokens=tthink,
            cost_usd=(tin * pin + (tout + tthink) * pout) / 1e6,
            latency_s=time.time() - t0,
            structured_mode="response_schema",
            params={"temperature": 0},
        )


class OpenRouterClient:
    api = "openrouter"

    # Reasoning models on OpenRouter reject `temperature` when parameters are
    # required, so they run at the provider default (probed 2026-09-22).
    NO_TEMPERATURE = {"anthropic/claude-opus-5", "openai/gpt-5.6-terra"}
    # Anthropic compiles json_schema response formats (strict or not) into a grammar and
    # refuses schemas with more than 16 nullable fields; ours has 42. Those models get the
    # same schema as a forced tool call instead, validated by Pydantic afterwards.
    TOOL_ROUTE = {"anthropic/claude-opus-5"}

    def __init__(self):
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
        self.headers = {
            "Authorization": f"Bearer {os.environ['OPEN_ROUTER_KEY']}",
            "X-Title": "tech-panic-tracker extraction benchmark",
        }

    @retrying
    def _post(self, body: dict) -> dict:
        r = httpx.post(f"{OPENROUTER}/v1/chat/completions", headers=self.headers, json=body, timeout=httpx.Timeout(1800, connect=30))
        if r.status_code >= 500 or r.status_code == 429:
            r.raise_for_status()
        d = r.json()
        if "error" in d:
            code = d["error"].get("code")
            if code in (429, 500, 502, 503, 504):
                raise httpx.HTTPStatusError(str(d["error"]), request=r.request, response=httpx.Response(code))
            raise RuntimeError(f"OpenRouter error {code}: {d['error'].get('message')}")
        return d

    def complete(self, model: str, system: str, user: str, schema: type[BaseModel]) -> CallResult:
        body = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": 64_000,
            "provider": {"require_parameters": True},
            "usage": {"include": True},
        }
        if model in self.TOOL_ROUTE:
            body["tools"] = [{"type": "function", "function": {"name": "submit", "description": f"Submit the {schema.__name__}", "parameters": strict_json_schema(schema)}}]
            body["tool_choice"] = {"type": "function", "function": {"name": "submit"}}
            mode = "tool_call"
        else:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": schema.__name__, "strict": True, "schema": strict_json_schema(schema)}}
            mode = "json_schema"
        params = {"max_tokens": 64_000}
        if model not in self.NO_TEMPERATURE:
            body["temperature"] = 0
            params["temperature"] = 0
        t0 = time.time()
        d = self._post(body)
        msg = d["choices"][0]["message"]
        text = msg["tool_calls"][0]["function"]["arguments"] if mode == "tool_call" else (msg.get("content") or "")
        u = d.get("usage", {})
        warnings = []
        if d["choices"][0].get("finish_reason") not in ("stop", None):
            warnings.append(f"finish_reason={d['choices'][0].get('finish_reason')}")
        return CallResult(
            text=text,
            parsed=schema.model_validate_json(text),
            model_version=d.get("model"),
            provider=d.get("provider"),
            input_tokens=u.get("prompt_tokens", 0),
            output_tokens=u.get("completion_tokens", 0),
            reasoning_tokens=(u.get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0,
            cost_usd=u.get("cost"),
            latency_s=time.time() - t0,
            structured_mode=mode,
            params=params,
            warnings=warnings,
        )


class JevClient:
    """typesafe/jev-1.13 via OpenRouter's decisions endpoint (format established by probe, 2026-09-22).

    Request: {model, state, questions: {id: {type: "choice", instructions, criteria: {option: description}}}}
    Response: {model, answers: {id: {type, choice, probabilities: {option: p}, confidence}}, usage: {cost}}
    """

    api = "openrouter"
    model = "typesafe/jev-1.13"

    def __init__(self):
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
        self.headers = {"Authorization": f"Bearer {os.environ['OPEN_ROUTER_KEY']}"}

    @retrying
    def ask(self, state: str, questions: dict) -> dict:
        r = httpx.post(f"{OPENROUTER}/alpha/decisions", headers=self.headers, json={"model": self.model, "state": state, "questions": questions}, timeout=120)
        if r.status_code >= 500 or r.status_code == 429:
            r.raise_for_status()
        d = r.json()
        if "error" in d:
            raise RuntimeError(f"Jev error: {d['error'].get('message')}")
        return d


def call_result_record(res: CallResult) -> dict:
    d = asdict(res)
    d.pop("parsed")
    d.pop("text")
    return d
