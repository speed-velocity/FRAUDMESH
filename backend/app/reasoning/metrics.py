from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from statistics import mean
from threading import Lock
from typing import Any


class LLMMetricStore:
    """Process-local, bounded telemetry for live model calls.

    Deliberately stores only operational metadata. Prompts, completions, evidence,
    user messages, and error text are never accepted by this store.
    """

    def __init__(self, maximum: int = 500) -> None:
        self._calls: deque[dict[str, Any]] = deque(maxlen=maximum)
        self._lock = Lock()

    def record(self, *, feature: str, model: str, status: str, latency_ms: float,
               ttft_ms: float | None = None, prompt_tokens: int | None = None,
               completion_tokens: int | None = None, total_tokens: int | None = None,
               tool_calls: int = 0, retries: int = 0, error_type: str | None = None) -> None:
        safe_status = status if status in {"ok", "error", "timeout"} else "error"
        item = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "feature": str(feature)[:40], "model": str(model)[:160], "status": safe_status,
            "latency_ms": round(max(0.0, float(latency_ms)), 2),
            "ttft_ms": round(float(ttft_ms), 2) if ttft_ms is not None else None,
            "prompt_tokens": prompt_tokens if isinstance(prompt_tokens, int) else None,
            "completion_tokens": completion_tokens if isinstance(completion_tokens, int) else None,
            "total_tokens": total_tokens if isinstance(total_tokens, int) else None,
            "tool_calls": max(0, int(tool_calls)), "retries": max(0, int(retries)),
            "error_type": error_type if error_type in {"http", "timeout", "invalid_response", "configuration", "unknown"} else None,
        }
        with self._lock:
            self._calls.append(item)

    def snapshot(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._calls)

    def summary(self) -> dict[str, Any]:
        calls = self.snapshot()
        latencies = sorted(item["latency_ms"] for item in calls)
        successful = [item for item in calls if item["status"] == "ok"]

        def percentile(values: list[float], percentile_value: float) -> float | None:
            if not values:
                return None
            index = min(len(values) - 1, max(0, round((len(values) - 1) * percentile_value)))
            return round(values[index], 2)

        def average(key: str) -> float | None:
            values = [item[key] for item in calls if item[key] is not None]
            return round(mean(values), 2) if values else None

        token_rates = []
        for item in successful:
            if item["completion_tokens"] and item["latency_ms"] > 0:
                token_rates.append(item["completion_tokens"] / (item["latency_ms"] / 1000))
        return {
            "requests": len(calls), "success_rate": round(len(successful) / len(calls), 3) if calls else 0,
            "p50_latency_ms": percentile(latencies, 0.50), "p95_latency_ms": percentile(latencies, 0.95),
            "avg_latency_ms": round(mean(latencies), 2) if latencies else None,
            "avg_ttft_ms": average("ttft_ms"), "avg_prompt_tokens": average("prompt_tokens"),
            "avg_completion_tokens": average("completion_tokens"), "avg_total_tokens": average("total_tokens"),
            "tokens_per_second": round(mean(token_rates), 2) if token_rates else None,
            "model": calls[-1]["model"] if calls else None,
            "since_timestamp": calls[0]["timestamp"] if calls else None,
        }


llm_metrics = LLMMetricStore()
