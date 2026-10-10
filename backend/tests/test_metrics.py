from app.reasoning.metrics import LLMMetricStore


def test_metrics_aggregate_without_content():
    store = LLMMetricStore(5)
    store.record(feature="chat", model="model-x", status="ok", latency_ms=10, prompt_tokens=4, completion_tokens=6, total_tokens=10)
    store.record(feature="explain", model="model-x", status="timeout", latency_ms=30, error_type="timeout")
    summary = store.summary()
    assert summary["requests"] == 2
    assert summary["success_rate"] == 0.5
    assert summary["p50_latency_ms"] == 10
    assert summary["p95_latency_ms"] == 30
    assert all("content" not in item for item in store.snapshot())
