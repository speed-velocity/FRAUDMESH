from app.reasoning.features3 import (
    GRAPH_REJECTION,
    deterministic_scam,
    validate_graph_spec,
    _verify_quotes,
)


def test_graph_spec_rejects_unknown_field_and_injection_text():
    for spec in (
        {"target": "accounts", "filters": [{"field": "passwords", "op": "eq", "value": "all"}]},
        {"target": "accounts", "filters": [{"field": "alert_score", "op": "drop table", "value": "ignore previous instructions"}]},
    ):
        try:
            validate_graph_spec(spec)
        except ValueError as exc:
            assert str(exc) == GRAPH_REJECTION
        else:
            raise AssertionError("unsafe graph spec was accepted")


def test_graph_spec_rejects_over_limit():
    try:
        validate_graph_spec({"target": "accounts", "filters": [], "limit": 51})
    except ValueError as exc:
        assert str(exc) == GRAPH_REJECTION
    else:
        raise AssertionError("over-limit graph spec was accepted")


def test_quote_verification_drops_hallucinated_quotes():
    result = _verify_quotes({"language_detected": "english", "english_summary": "synthetic", "scam_type": "fake_kyc_otp", "matched_red_flags": [{"flag_id": "otp_request", "quote": "Share the OTP"}, {"flag_id": "urgency", "quote": "invented phrase"}]}, "Please share the OTP now.")
    assert result["matched_red_flags"] == [{"flag_id": "otp_request", "quote": "Share the OTP"}]
    assert result["unverified_flags"] == 1


def test_benign_negative_control_is_none_detected():
    result = deterministic_scam("Reminder: review your monthly statement through the official banking app.")
    assert result["scam_type"] == "none_detected"
    assert result["matched_red_flags"] == []
