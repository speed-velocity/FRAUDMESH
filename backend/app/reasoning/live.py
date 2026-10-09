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


def _normalise_payload(payload: dict) -> dict:
    """Accept common OpenAI/model wrappers without weakening evidence checks."""
    for key in ("output", "result", "data"):
        nested = payload.get(key)
        if isinstance(nested, dict) and any(name in nested for name in ("summary", "findings", "suspicious_patterns", "recommended_checks")):
            return nested
    return payload


def _text_from_payload(payload: dict) -> str:
    for key in ("summary", "explanation", "analysis", "reasoning", "narrative", "text", "response", "message"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _is_meta_summary(summary: str) -> bool:
    lowered = summary.lower()
    return any(phrase in lowered for phrase in (
        "i'll make it",
        "i will make it",
        "in json",
        "3-4 concise",
        "the requested schema",
        "as requested",
    ))


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
            "summary": "string: 3-4 concise evidence-grounded sentences explaining the observed case sequence",
            "suspicious_patterns": ["object: {pattern: string, evidence_ids: string[], confidence: number}"],
            "recommended_checks": ["object: {check: string, rationale: string, evidence_ids: string[]}"],
            "cited_evidence_ids": ["string: only IDs from allowed_evidence_ids"],
        },
        "allowed_evidence_ids": sorted(allowed),
        "evidence": mask_prompt_records(records),
    }
    result = await client.complete([
        {"role": "system", "content": "Return only one valid JSON object matching the requested schema. Populate summary with the actual evidence-grounded explanation now; do not return a schema description, placeholder, formatting plan, or instructions to another writer. Use 3-4 concise sentences. Never mention JSON or invent evidence IDs or facts. If the evidence is insufficient, say that the linked evidence is insufficient and recommend human review."},
        {"role": "user", "content": json.dumps(prompt, ensure_ascii=True)},
    ])
    if result.status != "complete" or not result.content:
        raise ValueError(result.error or "Nemotron request was unavailable")
    try:
        payload = _parse_json(result.content)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("Nemotron returned invalid JSON") from exc
    payload = _normalise_payload(payload)

    cited = [item for item in payload.get("cited_evidence_ids", []) if item in allowed]
    withheld = len(payload.get("cited_evidence_ids", [])) - len(cited)
    findings = []
    for item in payload.get("suspicious_patterns", payload.get("findings", [])):
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
    for rank, item in enumerate(payload.get("recommended_checks", payload.get("plan_steps", [])), 1):
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
    summary = _text_from_payload(payload)
    if _is_meta_summary(summary):
        summary = ""
    if not summary and findings:
        summary = " ".join(item["statement"] for item in findings[:3])
    if not summary and plan_steps:
        summary = "Recommended checks: " + "; ".join(item["action"] for item in plan_steps[:3])
    if not summary:
        summary = "Nemotron returned no grounded explanation for this case. Review the linked evidence manually before making a determination."

    return {
        "case_id": case_id,
        "mode": "live",
        "label": "Live Nemotron · Nebius Token Factory",
        "summary": summary,
        "findings": findings,
        "hypotheses": [],
        "plan_steps": plan_steps,
        "cited_evidence_ids": cited,
        "withheld_count": withheld,
        "human_review_required": True,
        "recording_label": "Live result (not a cached recording)",
    }
