import pytest

from app.auth.token_factory import NimbusTokenFactory, TokenError


def test_nimbus_token_round_trip_and_claims():
    factory = NimbusTokenFactory("x" * 32)
    token, issued = factory.issue(user_id="USR-1", username="investigator", role="investigator", lifetime_seconds=600, now=100)
    claims = factory.verify(token, now=101)
    assert claims.jti == issued.jti
    assert claims.issuer == "fraudmesh"
    assert claims.audience == "fraudmesh-api"


def test_nimbus_rejects_tamper_and_expiry():
    factory = NimbusTokenFactory("x" * 32)
    token, _ = factory.issue(user_id="USR-1", username="investigator", role="investigator", lifetime_seconds=60, now=100)
    head, body, signature = token.split(".")
    with pytest.raises(TokenError):
        factory.verify(f"{head}.{body}.bad", now=101)
    with pytest.raises(TokenError):
        factory.verify(token, now=1000)
