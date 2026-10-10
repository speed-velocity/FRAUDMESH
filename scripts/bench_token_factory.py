"""Small, opt-in live benchmark. It never prints the API key or model output."""
from __future__ import annotations

import argparse
import asyncio
import os
import statistics
import time

import httpx


async def call(client: httpx.AsyncClient, url: str, headers: dict[str, str], model: str) -> float:
    started = time.perf_counter()
    response = await client.post(url, headers=headers, json={"model": model, "messages": [{"role": "user", "content": "Reply with the single word READY."}], "max_tokens": 8, "temperature": 0})
    response.raise_for_status()
    return (time.perf_counter() - started) * 1000


async def main() -> None:
    parser = argparse.ArgumentParser(description="Measure live Nebius Token Factory latency")
    parser.add_argument("-n", type=int, default=3, help="sequential calls")
    parser.add_argument("-m", type=int, default=2, help="concurrent calls")
    args = parser.parse_args()
    base = os.environ.get("NEMOTRON_BASE_URL", "").rstrip("/")
    key = os.environ.get("NEMOTRON_API_KEY", "")
    model = os.environ.get("NEMOTRON_MODEL", "")
    if not base or not key or not model:
        raise SystemExit("Set NEMOTRON_BASE_URL, NEMOTRON_API_KEY, and NEMOTRON_MODEL first.")
    url = f"{base}/chat/completions" if base.endswith("/v1") else f"{base}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=90) as client:
        sequential = [await call(client, url, headers, model) for _ in range(max(0, args.n))]
        started = time.perf_counter()
        concurrent = await asyncio.gather(*(call(client, url, headers, model) for _ in range(max(0, args.m))))
        elapsed = (time.perf_counter() - started) * 1000
    values = sequential + concurrent
    print(f"calls={len(values)} sequential={len(sequential)} concurrent={len(concurrent)}")
    if values:
        print(f"latency_ms_avg={statistics.mean(values):.2f} p50={statistics.median(values):.2f} max={max(values):.2f}")
    if concurrent:
        print(f"concurrent_wall_ms={elapsed:.2f} throughput_per_second={len(concurrent) / (elapsed / 1000):.2f}")


if __name__ == "__main__":
    asyncio.run(main())
