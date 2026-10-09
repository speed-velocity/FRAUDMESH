from __future__ import annotations

import json
import re

from app.db.database import case_evidence
from app.reasoning.client import NemotronClient
from app.reasoning.validator import mask_prompt_records


def _parse_json(content: str) -> dict:
    """Extract the first JSON object from a model response.

    Reasoning models may wrap the requested object in markdown fences, a
    short preamble, or a private ``<think>`` block.  We still require a real
    JSON object; downstream evidence validation remains the source of truth.
    """
    cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.I | re.S).strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I | re.S).strip()
    decoder = json.JSONDecoder()
    for index, character in enumerate(cleaned):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("Nemotron response must contain a JSON object")


async def run_live_reasoning(database_url: str, case_id: str, client: NemotronClient) -> dict:
    records = case_evidence(database_url, case_id)
    if not records:
        raise ValueError("case has no linked evidence")
    allowed = {record["evidence_id"] for record in records}
    prompt = {
        "task": "investigation_reasoning",
        "case_id": case_id,
        "policy": "Investigator support only. Do not state guilt, intent, or an enforcement decision. Use cautious language.",
        "output_schema": {
            "summary": "3-4 concise lines",
            "suspicious_patterns": ["objects with pattern, evidence_ids, confidence"],
            "recommended_checks": ["objects with check, rationale, evidence_ids"],
            "cited_evidence_ids": ["only IDs from allowed_evidence_ids"],
        },
        "allowed_evidence_ids": sorted(allowed),
        "evidence": mask_prompt_records(records),
    }
    result = await client.complete([
        {"role": "system", "content": "Return only valid JSON matching the requested schema. Never invent evidence IDs or facts."},
        {"role": "user", "content": json.dumps(prompt, ensure_ascii=True)},
    ])
    if result.status != "complete" or not result.content:
        raise ValueError(result.error or "Nemotron request was unavailable")
    try:
        payload = _parse_json(result.content)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("Nemotron returned invalid JSON") from exc

    cited = [item for item in payload.get("cited_evidence_ids", []) if item in allowed]
    withheld = len(payload.get("cited_evidence_ids", [])) - len(cited)
    findings = []
    for item in payload.get("suspicious_patterns", []):
        if not isinstance(item, dict):
            withheld += 1
            continue
        evidence_ids = [value for value in item.get("evidence_ids", []) if value in allowed]
        statement = str(item.get("pattern", item.get("statement", ""))).strip()
        if not statement or not evidence_ids:
            withheld += 1
            continue
        findings.append({
            "statement": statement,
            "evidence_ids": sorted(set(evidence_ids)),
            "entity_ids": [],
            "source": "Nemotron-live",
            "confidence": max(0.0, min(float(item.get("confidence", 0.5)), 1.0)),
            "review_state": "pending",
        })
    plan_steps = []
    for rank, item in enumerate(payload.get("recommended_checks", []), 1):
        if not isinstance(item, dict):
            continue
        action = str(item.get("check", item.get("action", ""))).strip()
        if action:
            plan_steps.append({
                "rank": rank,
                "action": action,
                "rationale": str(item.get("rationale", "Human review recommended.")).strip(),
                "evidence_ids": [value for value in item.get("evidence_ids", []) if value in allowed],
                "review_state": "pending",
            })
    return {
        "case_id": case_id,
        "mode": "live",
        "label": "Live Nemotron · Nebius Token Factory",
        "summary": str(payload.get("summary", "")).strip(),
        "findings": findings,
        "hypotheses": [],
        "plan_steps": plan_steps,
        "cited_evidence_ids": cited,
        "withheld_count": withheld,
        "human_review_required": True,
        "recording_label": "Live result (not a cached recording)",
    }
