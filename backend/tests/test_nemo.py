import json
import re
from pathlib import Path

from app.db.database import load_dataset
from app.reasoning.nemo import ACTION_REFUSAL, FOOTER, GUILT_REFUSAL, build_server_context, refusal_for_message, validate_nemo_payload, validate_page_context


def test_page_context_accepts_ids_only():
    assert validate_page_context({"case_id": "CASE-001", "evidence_id": "E-0093"}) == {"case_id": "CASE-001", "evidence_id": "E-0093"}
    try:
        validate_page_context({"case_id": "CASE-001", "facts": "untrusted"})
    except ValueError as exc:
        assert "IDs only" in str(exc)
    else:
        raise AssertionError("free-form page context was accepted")


def test_nemo_refuses_guilt_and_human_only_actions():
    assert refusal_for_message("Is ACC-M3 guilty?") == GUILT_REFUSAL
    assert refusal_for_message("Unmask E-0093") == ACTION_REFUSAL


def test_nemo_filters_invalid_citations_and_masks_context():
    database_path = Path(__file__).resolve().parent / "_api_tmp" / "nemo_unit.db"
    database_path.unlink(missing_ok=True)
    database = f"sqlite:///{database_path}"
    load_dataset(Path(__file__).resolve().parents[2] / "data" / "demo", database)
    context = build_server_context(database, {"evidence_id": "E-0093"})
    prompt = json.dumps(context)
    result = validate_nemo_payload({"answer": "Review the linked record [E-9999].", "citations": ["E-9999"]}, {"E-0093"}, set(), context)
    assert not re.search(r"(?<!\d)\d{9,18}(?!\d)", prompt)
    assert result["citations"] == []
    assert "E-9999" not in result["answer"]
    assert "not available" in result["answer"]
    assert FOOTER in result["answer"]
    database_path.unlink(missing_ok=True)
