from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx


@dataclass
class NemotronResult:
    status: str
    content: str | None = None
    error: str | None = None


class NemotronClient:
    def __init__(self, base_url: str = "", api_key: str = "", model: str = "", timeout_s: float = 90.0, max_retries: int = 2, max_tokens: int = 2048):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.max_tokens = max(256, max_tokens)

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)

    @property
    def completion_url(self) -> str:
        """Accept both a host base URL and an OpenAI-compatible `/v1` base URL."""
        return f"{self.base_url}/chat/completions" if self.base_url.endswith("/v1") else f"{self.base_url}/v1/chat/completions"

    async def complete(self, messages: list[dict], temperature: float = 0.0) -> NemotronResult:
        if not self.configured:
            return NemotronResult("unavailable", error="Nemotron endpoint, key, or model is not configured")
        payload = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": self.max_tokens}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                    response = await client.post(self.completion_url, json=payload, headers=headers)
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < self.max_retries:
                        await asyncio.sleep(0.25 * (2**attempt)); continue
                response.raise_for_status()
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if not isinstance(content, str):
                    return NemotronResult("invalid", error="Nemotron response did not contain message content")
                return NemotronResult("complete", content=content)
            except (httpx.HTTPError, ValueError) as exc:
                if attempt < self.max_retries:
                    await asyncio.sleep(0.25 * (2**attempt)); continue
                return NemotronResult("unavailable", error=str(exc))
        return NemotronResult("unavailable", error="Nemotron request failed")
