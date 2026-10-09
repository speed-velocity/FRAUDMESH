from __future__ import annotations

import re


def mask_prompt_records(records: list[dict]) -> list[dict]:
    """Remove raw contact/account-like values before a reasoning prompt is sent."""
    def clean(value: object) -> object:
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items()}
        if isinstance(value, list):
            return [clean(item) for item in value]
        if not isinstance(value, str):
            return value
        value = re.sub(r"(?<!\d)(?:\+?91[\s-]?)?[6-9](?:[\s-]?\d){9}(?!\d)", "[PHONE-MASKED]", value)
        value = re.sub(r"(?<!\d)\d{9,18}(?!\d)", "[ACCOUNT-MASKED]", value)
        return re.sub(r"([\w.+-]{2})[\w.+-]*(@[\w.-]+)", r"\1***\2", value)
    return [clean(record) for record in records]


def validate_reasoning(payload: dict, allowed_evidence_ids: set[str], allowed_entity_ids: set[str]) -> dict:
    """Drop unsupported model claims and return a safe, reviewable result."""
    findings = []
    withheld = 0
    for finding in payload.get("findings", []):
        if not isinstance(finding, dict):
            withheld += 1; continue
        evidence_ids = [item for item in finding.get("evidence_ids", []) if item in allowed_evidence_ids]
        entity_ids = [item for item in finding.get("entity_ids", []) if item in allowed_entity_ids]
        statement = str(finding.get("statement", "")).strip()
        if not statement or not evidence_ids:
            withheld += 1; continue
        if re.search(r"\b(guilty|criminal|fraudster|thief)\b", statement, re.I):
            statement = re.sub(r"\b(guilty|criminal|fraudster|thief)\b", "potentially relevant", statement, flags=re.I)
        findings.append({**finding, "statement": statement, "evidence_ids": evidence_ids, "entity_ids": entity_ids, "source": finding.get("source", "Nemotron-live")})
    hypotheses = [item for item in payload.get("hypotheses", []) if isinstance(item, dict) and any(evidence_id in allowed_evidence_ids for evidence_id in item.get("evidence_ids", []))]
    plan_steps = [item for item in payload.get("plan_steps", []) if isinstance(item, dict) and str(item.get("action", "")).strip()]
    return {"findings": findings, "hypotheses": hypotheses, "plan_steps": plan_steps, "summary": str(payload.get("summary", "")), "withheld_count": withheld}
