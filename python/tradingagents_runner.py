#!/usr/bin/env python3
import datetime as dt
import importlib.metadata
import json
import os
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Any


def _read_payload() -> dict[str, Any]:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON payload: {exc}") from exc


def _json_default(value: Any) -> str:
    return str(value)


def _emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, default=_json_default))


def _clean_optional_string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _today() -> str:
    return dt.date.today().isoformat()


def _format_decision(decision: Any) -> str:
    if isinstance(decision, str):
        return decision.strip()
    if isinstance(decision, dict):
        lines = []
        preferred_keys = [
            "decision",
            "action",
            "recommendation",
            "rating",
            "confidence",
            "risk_score",
            "reasoning",
            "rationale",
            "summary",
            "final_trade_decision",
        ]
        seen = set()
        for key in preferred_keys:
            if key in decision:
                seen.add(key)
                lines.append(f"**{key}**: {decision[key]}")
        for key, value in decision.items():
            if key not in seen:
                lines.append(f"**{key}**: {value}")
        return "\n".join(lines)
    return str(decision)


def _health() -> dict[str, Any]:
    try:
        version = importlib.metadata.version("tradingagents")
    except importlib.metadata.PackageNotFoundError:
        version = None

    return {
        "ok": version is not None,
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "tradingagentsVersion": version,
        "home": os.path.expanduser("~/.tradingagents"),
        "message": "TradingAgents is importable." if version else "TradingAgents is not installed in this Python environment.",
    }


def _build_config(payload: dict[str, Any]) -> dict[str, Any]:
    from tradingagents.default_config import DEFAULT_CONFIG

    config = DEFAULT_CONFIG.copy()

    string_overrides = {
        "llmProvider": "llm_provider",
        "deepThinkLlm": "deep_think_llm",
        "quickThinkLlm": "quick_think_llm",
        "backendUrl": "backend_url",
        "outputLanguage": "output_language",
    }
    for payload_key, config_key in string_overrides.items():
        value = _clean_optional_string(payload.get(payload_key))
        if value is not None:
            config[config_key] = value

    numeric_overrides = {
        "maxDebateRounds": "max_debate_rounds",
        "maxRiskRounds": "max_risk_discuss_rounds",
    }
    for payload_key, config_key in numeric_overrides.items():
        value = payload.get(payload_key)
        if isinstance(value, (int, float)):
            config[config_key] = int(value)

    if isinstance(payload.get("checkpoint"), bool):
        config["checkpoint_enabled"] = payload["checkpoint"]

    return config


def _analyze(payload: dict[str, Any]) -> dict[str, Any]:
    ticker = _clean_optional_string(payload.get("ticker"))
    if ticker is None:
        raise ValueError("ticker is required")

    analysis_date = _clean_optional_string(payload.get("analysisDate")) or _today()
    dt.date.fromisoformat(analysis_date)

    from tradingagents.graph.trading_graph import TradingAgentsGraph

    config = _build_config(payload)
    captured_stdout = StringIO()
    captured_stderr = StringIO()

    with redirect_stdout(captured_stdout), redirect_stderr(captured_stderr):
        graph = TradingAgentsGraph(debug=True, config=config)
        _, decision = graph.propagate(ticker.upper(), analysis_date)

    report = _format_decision(decision)
    markdown = "\n\n".join(
        [
            f"# TradingAgents: {ticker.upper()}",
            f"- Analysis date: {analysis_date}",
            f"- LLM provider: {config.get('llm_provider')}",
            f"- Deep model: {config.get('deep_think_llm')}",
            f"- Quick model: {config.get('quick_think_llm')}",
            "",
            "## Decision",
            report,
            "",
            "> Research output only. This is not financial, investment, or trading advice.",
        ]
    )

    return {
        "ok": True,
        "ticker": ticker.upper(),
        "analysisDate": analysis_date,
        "decision": decision,
        "markdown": markdown,
        "logs": {
            "stdoutTail": captured_stdout.getvalue()[-4000:],
            "stderrTail": captured_stderr.getvalue()[-4000:],
        },
        "config": {
            "llmProvider": config.get("llm_provider"),
            "deepThinkLlm": config.get("deep_think_llm"),
            "quickThinkLlm": config.get("quick_think_llm"),
            "outputLanguage": config.get("output_language"),
            "checkpoint": config.get("checkpoint_enabled"),
        },
    }


def main() -> int:
    payload = _read_payload()
    action = payload.get("action")
    try:
        if action == "health":
            _emit(_health())
            return 0
        if action == "analyze":
            _emit(_analyze(payload))
            return 0
        raise ValueError(f"Unknown action: {action!r}")
    except Exception as exc:
        _emit(
            {
                "ok": False,
                "error": str(exc),
                "traceback": traceback.format_exc(limit=8),
            }
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
