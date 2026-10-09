from app.reasoning.client import NemotronClient
from app.reasoning.validator import mask_prompt_records, validate_reasoning


def test_unconfigured_nemotron_degrades_gracefully():
    client = NemotronClient()
    assert client.configured is False


def test_nemotron_completion_url_accepts_both_base_url_forms():
    assert NemotronClient("https://example.test", "key", "model").completion_url == "https://example.test/v1/chat/completions"
    assert NemotronClient("https://example.test/v1", "key", "model").completion_url == "https://example.test/v1/chat/completions"


def test_validator_withholds_fabricated_and_accusatory_content():
    result = validate_reasoning({"findings": [
        {"statement": "The account is guilty", "evidence_ids": ["E-0001", "E-9999"], "entity_ids": ["ACC-M1"]},
        {"statement": "No citation", "evidence_ids": [], "entity_ids": []},
    ]}, {"E-0001"}, {"ACC-M1"})
    assert result["withheld_count"] == 1
    assert result["findings"][0]["evidence_ids"] == ["E-0001"]
    assert "guilty" not in result["findings"][0]["statement"].lower()


def test_prompt_records_mask_contact_and_account_like_values():
    masked = mask_prompt_records([{"text": "Call +91 90000 00101 or use 123456789012", "email": "analyst@example.com"}])[0]
    assert "90000 00101" not in masked["text"]
    assert "123456789012" not in masked["text"]
    assert "analyst@example.com" not in masked["email"]
