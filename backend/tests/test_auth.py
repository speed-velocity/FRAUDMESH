import pytest

from app.db.database import append_audit, authenticate_user, audit_records, connect, ensure_demo_users, revoke_session, session_user


def test_auth_session_revocation_and_audit(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'auth.db'}"
    ensure_demo_users(database_url, "investigator-pass", "admin-pass")
    user = authenticate_user(database_url, "investigator", "investigator-pass", session_minutes=60)
    assert user and user["role"] == "investigator"
    assert session_user(database_url, user["jti"])["username"] == "investigator"
    assert authenticate_user(database_url, "investigator", "wrong", session_minutes=60) is None
    append_audit(database_url, user["user_id"], user["role"], "case_view", "success", "req-1")
    assert audit_records(database_url)[0]["action"] == "case_view"
    connection = connect(database_url)
    try:
        with pytest.raises(Exception, match="append-only"):
            connection.execute("UPDATE audit_log SET outcome = 'tampered' WHERE audit_id = 1")
        with pytest.raises(Exception, match="append-only"):
            connection.execute("DELETE FROM audit_log WHERE audit_id = 1")
    finally:
        connection.close()
    revoke_session(database_url, user["jti"])
    assert session_user(database_url, user["jti"]) is None


def test_auth_lockout_after_five_failures(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'lockout.db'}"
    ensure_demo_users(database_url, "investigator-pass", "")
    for _ in range(5):
        assert authenticate_user(database_url, "investigator", "wrong", session_minutes=60) is None
    connection = connect(database_url)
    try:
        row = connection.execute("SELECT locked_until FROM users WHERE username = 'investigator'").fetchone()
        assert row["locked_until"]
    finally:
        connection.close()
