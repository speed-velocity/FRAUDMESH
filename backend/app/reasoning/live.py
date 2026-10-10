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
    for key in ("output", "result", "data", "response", "choices"):
        nested = payload.get(key)
        if isinstance(nested, dict):
            return _normalise_payload(nested)
        if isinstance(nested, list):
            for item in nested:
                if isinstance(item, dict):
                    return _normalise_payload(item)
    return payload


def _text_from_payload(payload: dict) -> str:
    for key in ("summary", "answer", "final", "final_answer", "explanation", "analysis", "reasoning", "reasoning_content", "narrative", "text", "content", "output_text", "generated_text", "completion", "response", "message", "choices"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, dict):
            nested = _text_from_payload(value)
            if nested:
                return nested
        if isinstance(value, list):
            parts = [item.strip() for item in value if isinstance(item, str) and item.strip()]
            if parts:
                return " ".join(parts)
            for item in value:
                if isinstance(item, dict):
                    nested = _text_from_payload(item)
                    if nested:
                        return nested
    return ""


def _evidence_fallback(records: list[dict]) -> str:
    total = sum(int(record.get("amount_inr") or 0) for record in records)
    timestamps = [str(record.get("ts_utc")) for record in records if record.get("ts_utc")]
    timing = f"from {min(timestamps)} through {max(timestamps)}" if timestamps else "with no complete timestamp range"
    citations = " ".join(f"[{record.get('evidence_id')}]" for record in records[:6] if record.get("evidence_id"))
    counterparties = sorted({str(record.get("from_entity")) for record in records if record.get("from_entity")} | {str(record.get("to_entity")) for record in records if record.get("to_entity")})
    counterparty_text = f" The linked records involve {len(counterparties)} recorded counterparties." if counterparties else " The linked counterparties are not fully established in the available records."
    return (
        f"The ledger contains {len(records)} linked transaction records totaling INR {total:,} {timing}.{counterparty_text} {citations} "
        f"The recorded sequence is a reviewable movement pattern, but these records alone do not establish coordination, intent, or guilt. {citations} "
        f"Compare the ledger timestamps, counterparties, and any independent case evidence before drawing a conclusion. {citations}"
    )


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


def _usable_plaintext_response(content: str, allowed: set[str]) -> str:
    """Accept a model's plain-text answer only when it cites supplied evidence."""
    cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.I | re.S)
    cleaned = re.sub(r"```(?:text|markdown)?", "", cleaned, flags=re.I).replace("```", "").strip()
    if not cleaned or _is_meta_summary(cleaned) or len(cleaned) < 40:
        return ""
    cited = {match.group(0) for match in re.finditer(r"\bE-\d{3,6}\b", cleaned)}
    if not cited or not cited.intersection(allowed):
        return ""
    if re.search(r"\b(guilty|fraudster|criminal|definitely fraud)\b", cleaned, re.I):
        return ""
    return cleaned[:2400]


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
    messages = [
        {"role": "system", "content": "Return only one valid JSON object matching the requested schema. Populate summary with the actual evidence-grounded explanation now; do not return a schema description, placeholder, formatting plan, or instructions to another writer. Use 3-4 concise sentences. Never mention JSON or invent evidence IDs or facts. If the evidence is insufficient, say that the linked evidence is insufficient and recommend human review."},
        {"role": "user", "content": json.dumps(prompt, ensure_ascii=True)},
    ]
    result = await client.complete(messages, feature="explain")
    if result.status != "complete" or not result.content:
        raise ValueError(result.error or "Nemotron request was unavailable")
    # A completed Token Factory request is not the same thing as a usable
    # grounded narrative. Keep that distinction explicit so the UI does not
    # report a successful provider call as an outage.
    fallback_reason = ""
    repair_used = False
    try:
        payload = _parse_json(result.content)
    except (json.JSONDecodeError, ValueError) as exc:
        plaintext = _usable_plaintext_response(result.content, allowed)
        if plaintext:
            payload = {"summary": plaintext, "suspicious_patterns": [], "recommended_checks": [], "cited_evidence_ids": sorted({item for item in allowed if item in plaintext})}
        else:
            fallback_reason = "invalid_or_uncited_model_output"
            repair_used = True
            repair = await client.complete([
                {"role": "system", "content": "Your previous output was unusable. Return one and only one valid JSON object now. The summary must contain 3-4 concrete, cautious sentences grounded in the supplied evidence IDs. Do not return a schema, preamble, markdown, or planning text."},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=True)},
            ], feature="explain")
            if repair.status != "complete" or not repair.content:
                raise ValueError("Nemotron returned invalid JSON") from exc
            try:
                payload = _parse_json(repair.content)
            except (json.JSONDecodeError, ValueError) as repair_exc:
                raise ValueError("Nemotron returned invalid JSON") from repair_exc
    payload = _normalise_payload(payload)
    initial_text = _text_from_payload(payload)
    structured_items = payload.get("suspicious_patterns", payload.get("findings", []))
    if (not initial_text.strip() or _is_meta_summary(initial_text)) and not structured_items and not repair_used:
        fallback_reason = "empty_or_schema_only_model_output"
        repair_used = True
        repair = await client.complete([
            {"role": "system", "content": "Return one valid JSON object now. Do not describe the schema. Write 3-4 concrete, cautious sentences in summary using only the supplied evidence IDs, then include empty arrays if no additional findings are supported."},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=True)},
        ], feature="explain")
        if repair.status == "complete" and repair.content:
            try:
                payload = _normalise_payload(_parse_json(repair.content))
            except (json.JSONDecodeError, ValueError):
                pass

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
    model_grounded = bool(summary.strip())
    if _is_meta_summary(summary):
        summary = ""
        model_grounded = False
        fallback_reason = fallback_reason or "meta_model_output"
    if not summary and findings:
        summary = " ".join(item["statement"] for item in findings[:3])
        model_grounded = True
    if not summary and plan_steps:
        summary = "Recommended checks: " + "; ".join(item["action"] for item in plan_steps[:3])
        model_grounded = True
    if not summary:
        fallback_reason = fallback_reason or "no_grounded_model_narrative"
        summary = _evidence_fallback(records)

    live_label = "Live Nemotron · Nebius Token Factory"
    fallback_label = "Live call succeeded · grounded server fallback"

    return {
        "case_id": case_id,
        "mode": "live",
        "label": live_label if model_grounded else fallback_label,
        "summary": summary,
        "findings": findings,
        "hypotheses": [],
        "plan_steps": plan_steps,
        "cited_evidence_ids": cited,
        "withheld_count": withheld,
        "human_review_required": True,
        "recording_label": "Live result (not a cached recording)" if model_grounded else "Grounded server fallback after a successful live call (not a cached recording)",
        "grounding_source": "nemotron" if model_grounded else "server_ledger_fallback",
        "repair_used": repair_used,
        "provider_call_succeeded": True,
        "fallback_reason": fallback_reason or None,
    }
