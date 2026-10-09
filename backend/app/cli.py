import argparse
import asyncio
import json
from pathlib import Path

from app.db.database import case_evidence, ensure_demo_users, load_dataset, list_cases
from app.core.config import get_settings
from app.reasoning.client import NemotronClient
from app.reasoning.validator import mask_prompt_records, validate_reasoning


def _parse_reasoning_json(content: str) -> dict:
    """Accept plain, fenced, or prefixed JSON while rejecting non-objects."""
    decoder = json.JSONDecoder()
    for index, character in enumerate(content):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(content[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise json.JSONDecodeError("No JSON object found in Nemotron response", content, 0)


def main() -> None:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True)
    seed = sub.add_parser("reset-and-seed"); seed.add_argument("--dataset", default="data/demo"); seed.add_argument("--database-url", default="sqlite:///data/runtime/fraudmesh.db")
    users = sub.add_parser("setup-demo-users"); users.add_argument("--investigator-password", required=True); users.add_argument("--admin-password", required=True); users.add_argument("--database-url", default="sqlite:///data/runtime/fraudmesh.db")
    smoke = sub.add_parser("nemotron-smoke", help="verify the configured OpenAI-compatible Nemotron endpoint"); smoke.add_argument("--prompt", default="Reply with the single word READY.")
    reasoning = sub.add_parser("record-reasoning"); reasoning.add_argument("--case", required=True, dest="case_id"); reasoning.add_argument("--database-url", default="sqlite:///data/runtime/fraudmesh.db"); reasoning.add_argument("--output", default="data/demo/cached_reasoning")
    args = parser.parse_args()
    if args.command == "reset-and-seed": print(json.dumps(load_dataset(args.dataset, args.database_url), indent=2))
    if args.command == "setup-demo-users": ensure_demo_users(args.database_url, args.investigator_password, args.admin_password); print(json.dumps({"status": "demo users configured", "usernames": ["investigator", "admin"]}, indent=2))
    if args.command == "nemotron-smoke":
        settings = get_settings()
        client = NemotronClient(settings.nemotron_base_url, settings.nemotron_api_key, settings.nemotron_model, settings.nemotron_timeout_s, max_tokens=settings.nemotron_max_tokens)
        if not client.configured:
            raise SystemExit("nemotron-smoke refused: configure NEMOTRON_BASE_URL, NEMOTRON_API_KEY, and NEMOTRON_MODEL")
        result = asyncio.run(client.complete([{"role": "system", "content": "Return only the requested word."}, {"role": "user", "content": args.prompt}]))
        if result.status != "complete":
            raise SystemExit(f"Nemotron unavailable: {result.error}")
        print(json.dumps({"status": "reachable", "model": settings.nemotron_model, "response_length": len(result.content or "")}, indent=2))
    if args.command == "record-reasoning":
        settings = get_settings()
        client = NemotronClient(settings.nemotron_base_url, settings.nemotron_api_key, settings.nemotron_model, settings.nemotron_timeout_s, max_tokens=settings.nemotron_max_tokens)
        if not client.configured:
            raise SystemExit("record-reasoning refused: configure NEMOTRON_BASE_URL, NEMOTRON_API_KEY, and NEMOTRON_MODEL")
        case = next((item for item in list_cases(args.database_url) if item["case_id"] == args.case_id), None)
        if not case:
            raise SystemExit(f"case not found: {args.case_id}")
        evidence = case_evidence(args.database_url, args.case_id)
        allowed = [item["evidence_id"] for item in evidence]
        prompt = {"task": "investigation_reasoning", "prompt_policy": "Identifiers and contact-like values are masked before transmission; evidence IDs are technical references only.", "case": case, "allowed_evidence_ids": allowed, "evidence": mask_prompt_records(evidence)}
        result = asyncio.run(client.complete([{"role": "system", "content": "Return one JSON object only; the first character must be { and the last character must be }. Do not use markdown fences or commentary. Exact schema: {\"summary\":\"...\",\"findings\":[{\"statement\":\"potential relationship\",\"evidence_ids\":[\"E-0001\"],\"entity_ids\":[\"ACC-M3\"]}],\"hypotheses\":[],\"plan_steps\":[]}. Use hedged investigation language and cite only allowed evidence IDs."}, {"role": "user", "content": json.dumps(prompt)}]))
        if result.status != "complete":
            raise SystemExit(f"Nemotron unavailable: {result.error}")
        try:
            validated = validate_reasoning(_parse_reasoning_json(result.content or ""), set(allowed), {case["entity_id"]})
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Nemotron returned invalid JSON: {exc}")
        output = Path(args.output); output.mkdir(parents=True, exist_ok=True); target = output / f"{args.case_id}.json"; target.write_text(json.dumps(validated, indent=2), encoding="utf-8")
        print(json.dumps({"status": "recorded", "case_id": args.case_id, "output": str(target), "withheld_count": validated["withheld_count"]}, indent=2))


if __name__ == "__main__": main()
