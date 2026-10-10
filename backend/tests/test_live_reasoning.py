import asyncio
from pathlib import Path

from app.db.database import create_case, load_dataset
from app.reasoning.live import run_live_reasoning
from app.reasoning.live import _parse_json


class FakeTokenFactoryClient:
    async def complete(self, messages):
        assert "E-" in messages[1]["content"]
        return type("Result", (), {"status": "complete", "content": '{"summary":"Review the linked movement.","suspicious_patterns":[{"pattern":"Repeated linked transfers warrant review.","evidence_ids":["E-0001"],"confidence":0.7}],"recommended_checks":[{"check":"Compare source timestamps.","rationale":"Confirm chronology.","evidence_ids":["E-0001"]}],"cited_evidence_ids":["E-0001","E-9999"]}', "error": None})()


def test_live_parser_accepts_reasoning_wrapper_and_markdown_fence():
    assert _parse_json('<think>internal reasoning</think>\n```json\n{"summary":"ready"}\n```') == {"summary": "ready"}


def test_live_reasoning_uses_validated_finding_when_summary_is_empty():
    class FindingOnlyClient:
        async def complete(self, messages):
            return type("Result", (), {"status": "complete", "content": '{"suspicious_patterns":[{"pattern":"Repeated linked transfers warrant review.","evidence_ids":["E-0001"]}],"cited_evidence_ids":["E-0001"]}', "error": None})()

    selector_policy = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if selector_policy:
        asyncio.set_event_loop_policy(selector_policy())
    database_path = Path(__file__).resolve().parent / "_api_tmp" / "live_reasoning_summary.db"
    database_path.unlink(missing_ok=True)
    database = f"sqlite:///{database_path}"
    dataset = Path(__file__).resolve().parents[2] / "data" / "demo"
    load_dataset(str(dataset), database)
    create_case(database, "ACC-M3", 80, "Review ACC-M3", "Investigator review")
    result = asyncio.run(run_live_reasoning(database, "CASE-001", FindingOnlyClient()))
    assert result["summary"] == "Repeated linked transfers warrant review."
    database_path.unlink(missing_ok=True)


def test_live_reasoning_accepts_nested_model_output():
    from app.reasoning.live import _normalise_payload, _text_from_payload

    payload = _normalise_payload({"output": {"reasoning": "Review the linked movement.", "findings": []}})
    assert _text_from_payload(payload) == "Review the linked movement."


def test_live_reasoning_accepts_openai_choice_wrapper():
    from app.reasoning.live import _normalise_payload, _text_from_payload

    payload = _normalise_payload({"choices": [{"message": {"content": "Review the linked movement."}}]})
    assert _text_from_payload(payload) == "Review the linked movement."


def test_live_reasoning_grounds_mocked_token_factory_response():
    selector_policy = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if selector_policy:
        asyncio.set_event_loop_policy(selector_policy())
    database_path = Path(__file__).resolve().parent / "_api_tmp" / "live_reasoning.db"
    database_path.unlink(missing_ok=True)
    database = f"sqlite:///{database_path}"
    dataset = Path(__file__).resolve().parents[2] / "data" / "demo"
    load_dataset(str(dataset), database)
    create_case(database, "ACC-M3", 80, "Review ACC-M3", "Investigator review")
    result = asyncio.run(run_live_reasoning(database, "CASE-001", FakeTokenFactoryClient()))
    assert result["mode"] == "live"
    assert result["label"].endswith("Nebius Token Factory")
    assert result["cited_evidence_ids"] == ["E-0001"]
    assert result["withheld_count"] == 1
    assert result["findings"][0]["source"] == "Nemotron-live"
    database_path.unlink(missing_ok=True)
