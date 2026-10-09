"""Nimbus-style signed access-token factory.

This is intentionally dependency-free so the demo can run from the bundled
Python environment.  It implements the JOSE-compatible pieces FraudMesh
needs: HS256 signing, key id, issuer/audience, expiry and unique JTIs.
Revocation remains server-side in the sessions table.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass


class TokenError(ValueError):
    """Raised when a token is malformed, invalid, or expired."""


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


@dataclass(frozen=True)
class TokenClaims:
    subject: str
    username: str
    role: str
    jti: str
    issued_at: int
    expires_at: int
    issuer: str
    audience: str


class NimbusTokenFactory:
    """Small, auditable access-token issuer/verifier for local deployments."""

    algorithm = "HS256"

    def __init__(self, secret: str, *, key_id: str = "fraudmesh-local-1", issuer: str = "fraudmesh", audience: str = "fraudmesh-api"):
        if not secret or len(secret) < 32:
            raise ValueError("Token signing secret must be at least 32 characters")
        self._secret = secret.encode("utf-8")
        self.key_id = key_id
        self.issuer = issuer
        self.audience = audience

    def issue(self, *, user_id: str, username: str, role: str, lifetime_seconds: int = 3600, now: int | None = None) -> tuple[str, TokenClaims]:
        issued = int(time.time() if now is None else now)
        claims = TokenClaims(user_id, username, role, secrets.token_urlsafe(18), issued, issued + max(60, lifetime_seconds), self.issuer, self.audience)
        header = {"alg": self.algorithm, "kid": self.key_id, "typ": "JWT"}
        payload = {"sub": claims.subject, "username": claims.username, "role": claims.role, "jti": claims.jti, "iat": claims.issued_at, "exp": claims.expires_at, "iss": claims.issuer, "aud": claims.audience}
        encoded_header = _encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode())
        encoded_payload = _encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
        unsigned = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = hmac.new(self._secret, unsigned, hashlib.sha256).digest()
        return f"{encoded_header}.{encoded_payload}.{_encode(signature)}", claims

    def verify(self, token: str, *, now: int | None = None) -> TokenClaims:
        try:
            encoded_header, encoded_payload, encoded_signature = token.split(".")
            header = json.loads(_decode(encoded_header))
            payload = json.loads(_decode(encoded_payload))
            expected = hmac.new(self._secret, f"{encoded_header}.{encoded_payload}".encode("ascii"), hashlib.sha256).digest()
            if header.get("alg") != self.algorithm or header.get("kid") != self.key_id or not hmac.compare_digest(_decode(encoded_signature), expected):
                raise TokenError("Invalid token signature")
            required = ("sub", "username", "role", "jti", "iat", "exp", "iss", "aud")
            if any(key not in payload for key in required) or payload["iss"] != self.issuer or payload["aud"] != self.audience:
                raise TokenError("Invalid token claims")
            current = int(time.time() if now is None else now)
            if int(payload["exp"]) <= current:
                raise TokenError("Token expired")
            return TokenClaims(str(payload["sub"]), str(payload["username"]), str(payload["role"]), str(payload["jti"]), int(payload["iat"]), int(payload["exp"]), str(payload["iss"]), str(payload["aud"]))
        except (ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise TokenError("Malformed token") from exc
