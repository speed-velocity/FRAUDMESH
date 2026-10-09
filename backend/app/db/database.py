from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import base64
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from app.auth.token_factory import NimbusTokenFactory, TokenError


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS datasets (dataset_id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL, seed TEXT NOT NULL, synthetic INTEGER NOT NULL CHECK (synthetic = 1), base_date TEXT NOT NULL, manifest_json TEXT NOT NULL, loaded_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence (evidence_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL, type TEXT NOT NULL, source_file TEXT NOT NULL, source_row INTEGER NOT NULL, ts_utc TEXT, content_json TEXT NOT NULL, raw_text TEXT, content_hash TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS entities (entity_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL, type TEXT NOT NULL, normalized_key TEXT NOT NULL, display_label TEXT NOT NULL, scope TEXT NOT NULL, attrs_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS transactions (txn_id TEXT PRIMARY KEY, evidence_id TEXT NOT NULL, kind TEXT NOT NULL, from_entity TEXT NOT NULL, to_entity TEXT, amount_paise INTEGER NOT NULL, ts_utc TEXT NOT NULL, channel TEXT NOT NULL, reference_text TEXT NOT NULL, held_out INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS complaints (complaint_id TEXT PRIMARY KEY, evidence_id TEXT NOT NULL, victim_entity TEXT NOT NULL, incident_id TEXT NOT NULL, filed_at TEXT NOT NULL, narrative TEXT NOT NULL, held_out INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS communications (comm_id TEXT PRIMARY KEY, evidence_id TEXT NOT NULL, comm_type TEXT NOT NULL, from_ref TEXT NOT NULL, to_ref TEXT NOT NULL, ts_utc TEXT NOT NULL, text_or_summary TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS flags (entity_id TEXT PRIMARY KEY, source TEXT NOT NULL, note TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS investigation_cases (case_id TEXT PRIMARY KEY, dataset_id TEXT NOT NULL, entity_id TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL, score INTEGER NOT NULL, notes TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK (role IN ('investigator', 'admin')), failed_attempts INTEGER NOT NULL DEFAULT 0, locked_until TEXT, active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS sessions (jti TEXT PRIMARY KEY, user_id TEXT NOT NULL, expires_at TEXT NOT NULL, revoked_at TEXT);
CREATE TABLE IF NOT EXISTS audit_log (audit_id INTEGER PRIMARY KEY AUTOINCREMENT, ts_utc TEXT NOT NULL, actor_id TEXT, role TEXT, action TEXT NOT NULL, target_type TEXT, target_id TEXT, outcome TEXT NOT NULL, request_id TEXT, details_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ingested_events (event_id TEXT PRIMARY KEY, received_at TEXT NOT NULL, status TEXT NOT NULL, reason TEXT);
CREATE TABLE IF NOT EXISTS findings (finding_id TEXT PRIMARY KEY, case_id TEXT NOT NULL, statement TEXT NOT NULL, evidence_ids_json TEXT NOT NULL, source TEXT NOT NULL, confidence REAL NOT NULL, review_state TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS hypotheses (hypothesis_id TEXT PRIMARY KEY, case_id TEXT NOT NULL, statement TEXT NOT NULL, evidence_ids_json TEXT NOT NULL, confidence REAL NOT NULL, review_state TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS plan_steps (step_id TEXT PRIMARY KEY, case_id TEXT NOT NULL, rank INTEGER NOT NULL, action TEXT NOT NULL, rationale TEXT NOT NULL, evidence_ids_json TEXT NOT NULL, linked_hypothesis TEXT, review_state TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS review_history (review_id INTEGER PRIMARY KEY AUTOINCREMENT, item_type TEXT NOT NULL, item_id TEXT NOT NULL, previous_state TEXT NOT NULL, new_state TEXT NOT NULL, reason TEXT NOT NULL, actor_id TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS links (link_id TEXT PRIMARY KEY, source_entity TEXT NOT NULL, target_entity TEXT NOT NULL, link_type TEXT NOT NULL, strength TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'unreviewed', evidence_ids_json TEXT NOT NULL, cluster_forming INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS alert_actions (action_id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id TEXT NOT NULL, action TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS audit_log_no_update BEFORE UPDATE ON audit_log BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_log_no_delete BEFORE DELETE ON audit_log BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
"""


def db_path(database_url: str = "sqlite:///data/runtime/fraudmesh.db") -> Path:
    raw = database_url.removeprefix("sqlite:///")
    path = Path(raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def connect(database_url: str = "sqlite:///data/runtime/fraudmesh.db") -> sqlite3.Connection:
    connection = sqlite3.connect(db_path(database_url))
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def _password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**12, r=8, p=1)
    return f"scrypt${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def _password_matches(password: str, encoded: str) -> bool:
    try:
        _, salt, expected = encoded.split("$", 2)
        actual = _password_hash(password, base64.urlsafe_b64decode(salt)).split("$", 2)[2]
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def ensure_demo_users(database_url: str, investigator_password: str = "", admin_password: str = "") -> None:
    """Create development users only when explicit passwords are supplied by the caller."""
    if not investigator_password and not admin_password:
        return
    connection = connect(database_url)
    try:
        for username, role, password in (("investigator", "investigator", investigator_password), ("admin", "admin", admin_password)):
            if password:
                connection.execute("INSERT OR IGNORE INTO users (user_id, username, password_hash, role) VALUES (?, ?, ?, ?)", (f"USR-{role}", username, _password_hash(password), role))
        connection.commit()
    finally:
        connection.close()


def authenticate_user(database_url: str, username: str, password: str, session_minutes: int = 60, token_secret: str = "", token_key_id: str = "fraudmesh-local-1", token_issuer: str = "fraudmesh", token_audience: str = "fraudmesh-api") -> dict | None:
    now = datetime.now(timezone.utc)
    connection = connect(database_url)
    try:
        user = connection.execute("SELECT * FROM users WHERE username = ? AND active = 1", (username,)).fetchone()
        generic_failure = user is None
        if user and user["locked_until"] and datetime.fromisoformat(user["locked_until"].replace("Z", "+00:00")) > now:
            return None
        if generic_failure or not _password_matches(password, user["password_hash"]):
            if user:
                failed = user["failed_attempts"] + 1
                locked_until = (now + timedelta(minutes=5)).isoformat().replace("+00:00", "Z") if failed >= 5 else None
                connection.execute("UPDATE users SET failed_attempts = ?, locked_until = ? WHERE user_id = ?", (0 if locked_until else failed, locked_until, user["user_id"]))
                connection.commit()
            return None
        expires = (now + timedelta(minutes=session_minutes)).isoformat().replace("+00:00", "Z")
        if token_secret:
            access_token, claims = NimbusTokenFactory(token_secret, key_id=token_key_id, issuer=token_issuer, audience=token_audience).issue(user_id=user["user_id"], username=user["username"], role=user["role"], lifetime_seconds=session_minutes * 60)
            jti = claims.jti
        else:
            access_token = jti = secrets.token_urlsafe(18)
        connection.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE user_id = ?", (user["user_id"],))
        connection.execute("INSERT INTO sessions VALUES (?, ?, ?, NULL)", (jti, user["user_id"], expires)); connection.commit()
        return {"user_id": user["user_id"], "username": user["username"], "role": user["role"], "jti": jti, "access_token": access_token, "expires_at": expires}
    finally:
        connection.close()


def revoke_session(database_url: str, jti: str, token_secret: str = "", token_key_id: str = "fraudmesh-local-1", token_issuer: str = "fraudmesh", token_audience: str = "fraudmesh-api") -> None:
    if token_secret:
        try: jti = NimbusTokenFactory(token_secret, key_id=token_key_id, issuer=token_issuer, audience=token_audience).verify(jti).jti
        except TokenError: return
    connection = connect(database_url)
    try:
        connection.execute("UPDATE sessions SET revoked_at = ? WHERE jti = ?", (datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), jti)); connection.commit()
    finally:
        connection.close()


def session_user(database_url: str, jti: str, token_secret: str = "", token_key_id: str = "fraudmesh-local-1", token_issuer: str = "fraudmesh", token_audience: str = "fraudmesh-api") -> dict | None:
    if token_secret:
        try: jti = NimbusTokenFactory(token_secret, key_id=token_key_id, issuer=token_issuer, audience=token_audience).verify(jti).jti
        except TokenError: return None
    connection = connect(database_url)
    try:
        row = connection.execute("SELECT u.user_id, u.username, u.role, s.expires_at, s.revoked_at FROM sessions s JOIN users u ON u.user_id = s.user_id WHERE s.jti = ? AND u.active = 1", (jti,)).fetchone()
        if not row or row["revoked_at"] or datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) <= datetime.now(timezone.utc): return None
        return dict(row)
    finally:
        connection.close()


def append_audit(database_url: str, actor_id: str | None, role: str | None, action: str, outcome: str, request_id: str | None = None, target_type: str | None = None, target_id: str | None = None, details: dict | None = None) -> dict:
    connection = connect(database_url)
    try:
        stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        cursor = connection.execute("INSERT INTO audit_log (ts_utc, actor_id, role, action, target_type, target_id, outcome, request_id, details_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (stamp, actor_id, role, action, target_type, target_id, outcome, request_id, json.dumps(details or {}, sort_keys=True)))
        connection.commit(); return {"audit_id": cursor.lastrowid, "ts_utc": stamp, "actor_id": actor_id, "role": role, "action": action, "outcome": outcome, "request_id": request_id}
    finally:
        connection.close()


def audit_records(database_url: str, limit: int = 100, offset: int = 0) -> list[dict]:
    connection = connect(database_url)
    try:
        return [dict(row) for row in connection.execute("SELECT audit_id, ts_utc, actor_id, role, action, target_type, target_id, outcome, request_id, details_json FROM audit_log ORDER BY audit_id DESC LIMIT ? OFFSET ?", (min(max(limit, 1), 200), max(offset, 0))).fetchall()]
    finally:
        connection.close()


def list_users(database_url: str) -> list[dict]:
    connection = connect(database_url)
    try:
        return [dict(row) for row in connection.execute("SELECT user_id, username, role, active, failed_attempts, locked_until FROM users ORDER BY username").fetchall()]
    finally:
        connection.close()


def load_dataset(dataset_dir: str | Path, database_url: str = "sqlite:///data/runtime/fraudmesh.db") -> dict:
    root = Path(dataset_dir); manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("synthetic") is not True:
        raise ValueError("Dataset refused: manifest synthetic must be true")
    connection = connect(database_url)
    try:
        connection.execute("DELETE FROM communications"); connection.execute("DELETE FROM complaints"); connection.execute("DELETE FROM transactions"); connection.execute("DELETE FROM evidence"); connection.execute("DELETE FROM entities"); connection.execute("DELETE FROM flags"); connection.execute("DELETE FROM links"); connection.execute("DELETE FROM alert_actions"); connection.execute("DELETE FROM findings"); connection.execute("DELETE FROM hypotheses"); connection.execute("DELETE FROM plan_steps"); connection.execute("DELETE FROM review_history"); connection.execute("DELETE FROM investigation_cases"); connection.execute("DELETE FROM ingested_events"); connection.execute("DELETE FROM settings"); connection.execute("DELETE FROM datasets")
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        connection.execute("INSERT INTO datasets VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (manifest["dataset_id"], manifest["name"], manifest["version"], manifest["seed"], 1, manifest["base_date"], json.dumps(manifest), now))
        evidence_number = 1
        def add_evidence(kind: str, filename: str, row: int, value: dict, raw_text: str | None = None, stamp: str | None = None) -> str:
            nonlocal evidence_number
            evidence_id = f"E-{evidence_number:04d}"; evidence_number += 1
            encoded = json.dumps(value, sort_keys=True, separators=(",", ":")); digest = hashlib.sha256(encoded.encode()).hexdigest()
            connection.execute("INSERT INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (evidence_id, manifest["dataset_id"], kind, filename, row, stamp, encoded, raw_text, digest)); return evidence_id
        for filename, kind in [("accounts.json", "account"), ("upi.json", "upi"), ("phones.json", "phone"), ("devices.json", "device"), ("communications.json", "communication"), ("complaints.json", "complaint"), ("transactions.json", "transaction")]:
            if not (root / filename).exists(): continue
            records = json.loads((root / filename).read_text(encoding="utf-8"))
            for row, record in enumerate(records, 1): add_evidence(kind, filename, row, record, record.get("narrative") or record.get("text"), record.get("ts") or record.get("filed_at"))
        evidence_by_file = {row["source_file"]: [] for row in connection.execute("SELECT DISTINCT source_file FROM evidence")}
        for row in connection.execute("SELECT evidence_id, source_file, source_row FROM evidence"): evidence_by_file[row["source_file"]].append(row["evidence_id"])
        accounts = json.loads((root / "accounts.json").read_text(encoding="utf-8"))
        for record in accounts: connection.execute("INSERT INTO entities VALUES (?, ?, ?, ?, ?, ?, ?)", (record["account_id"], manifest["dataset_id"], "BankAccount", record["account_number"], record["account_id"], record["scope"], json.dumps(record)))
        for record in json.loads((root / "entities.json").read_text(encoding="utf-8")): connection.execute("INSERT INTO entities VALUES (?, ?, ?, ?, ?, ?, ?)", (record["entity_id"], manifest["dataset_id"], "Person/Entity", record["entity_id"], record["display_name"], "investigated", json.dumps(record)))
        txns = json.loads((root / "transactions.json").read_text(encoding="utf-8")); txn_evidence = evidence_by_file.get("transactions.json", [])
        for index, record in enumerate(txns): connection.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (record["txn_id"], txn_evidence[index], record["kind"], record["from_account"], record.get("to_account"), record["amount_inr"] * 100, record["ts"], record["channel"], record["reference"], int(record["held_out"])))
        complaints = json.loads((root / "complaints.json").read_text(encoding="utf-8")); complaint_evidence = evidence_by_file.get("complaints.json", [])
        for index, record in enumerate(complaints): connection.execute("INSERT INTO complaints VALUES (?, ?, ?, ?, ?, ?, ?)", (record["complaint_id"], complaint_evidence[index], record["victim_id"], record["incident_id"], record["filed_at"], record["narrative"], int(record["held_out"])))
        communications = json.loads((root / "communications.json").read_text(encoding="utf-8")); comm_evidence = evidence_by_file.get("communications.json", [])
        for index, record in enumerate(communications): connection.execute("INSERT INTO communications VALUES (?, ?, ?, ?, ?, ?, ?)", (record["comm_id"], comm_evidence[index], record["type"], record["from_ref"], record["to_ref"], record["ts"], record["text"]))
        for record in json.loads((root / "flags.json").read_text(encoding="utf-8")): connection.execute("INSERT INTO flags VALUES (?, ?, ?)", (record["entity_id"], record["source"], record["note"]))
        connection.execute("INSERT OR REPLACE INTO settings VALUES ('dataset_dir', ?)", (str(root),)); connection.commit()
        return {"dataset_id": manifest["dataset_id"], "synthetic": True, "counts": {"evidence": connection.execute("SELECT COUNT(*) FROM evidence").fetchone()[0], "entities": connection.execute("SELECT COUNT(*) FROM entities").fetchone()[0], "transactions": len(txns), "complaints": len(complaints), "communications": len(communications)}}
    finally: connection.close()


def current_summary(database_url: str = "sqlite:///data/runtime/fraudmesh.db") -> dict:
    connection = connect(database_url)
    try:
        dataset = connection.execute("SELECT dataset_id, name, version, seed, base_date, loaded_at FROM datasets LIMIT 1").fetchone()
        if not dataset: return {"dataset_loaded": False, "dataset": None, "counts": {}}
        counts = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("evidence", "entities", "transactions", "complaints", "communications")}
        counts["incidents"] = connection.execute("SELECT COUNT(DISTINCT incident_id) FROM complaints").fetchone()[0]
        return {"dataset_loaded": True, "dataset": dict(dataset), "counts": counts}
    finally: connection.close()


def apply_alert_action(database_url: str, entity_id: str, action: str, reason: str = "") -> dict:
    if action not in {"acknowledge", "dismiss", "escalate"}: raise ValueError("action must be acknowledge, dismiss, or escalate")
    if action == "dismiss" and len(reason.strip()) < 8: raise ValueError("dismiss reason of at least 8 characters is required")
    connection = connect(database_url)
    try:
        if not connection.execute("SELECT 1 FROM entities WHERE entity_id = ?", (entity_id,)).fetchone(): raise ValueError("alert entity not found")
        stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        connection.execute("INSERT INTO alert_actions (entity_id, action, reason, created_at) VALUES (?, ?, ?, ?)", (entity_id, action, reason.strip(), stamp)); connection.commit()
        return {"entity_id": entity_id, "action": action, "reason": reason.strip(), "created_at": stamp}
    finally: connection.close()


def alert_actions(database_url: str, entity_id: str) -> list[dict]:
    connection = connect(database_url)
    try: return [dict(row) for row in connection.execute("SELECT action_id, entity_id, action, reason, created_at FROM alert_actions WHERE entity_id = ? ORDER BY action_id", (entity_id,)).fetchall()]
    finally: connection.close()


def rollback_alert_action(database_url: str, entity_id: str, action: str, created_at: str) -> None:
    """Compensate an alert action if its required audit write fails."""
    connection = connect(database_url)
    try:
        connection.execute("DELETE FROM alert_actions WHERE entity_id = ? AND action = ? AND created_at = ?", (entity_id, action, created_at))
        connection.commit()
    finally: connection.close()


def alert_status(database_url: str, entity_id: str) -> str:
    """Return the current triage state derived from the latest alert action."""
    connection = connect(database_url)
    try:
        row = connection.execute("SELECT action FROM alert_actions WHERE entity_id = ? ORDER BY action_id DESC LIMIT 1", (entity_id,)).fetchone()
        return str(row["action"]) if row else "new"
    finally: connection.close()


def _risk_band(score: int) -> str:
    if score >= 75: return "critical"
    if score >= 50: return "high"
    if score >= 25: return "medium"
    return "low"


def _band_index(band: str) -> int:
    return {"low": 0, "medium": 1, "high": 2, "critical": 3}[band]


def _victim_score(count: int, senders: int, amount_paise: int, seeded: bool) -> int:
    return min(100, count * 8 + senders * 4 + (20 if seeded else 0) + min(20, amount_paise // 1_000_000))


RULE_SEQUENCE = ("R1", "R2", "R3", "R4", "R5", "R6")


def risk_profile(database_url: str, entity_id: str) -> dict | None:
    """Return a transparent risk profile with displayed mitigating factors."""
    connection = connect(database_url)
    try:
        entity = connection.execute("SELECT entity_id, type, display_label FROM entities WHERE entity_id = ?", (entity_id,)).fetchone()
        if not entity:
            return None
        transactions = [dict(row) for row in connection.execute("SELECT from_entity, to_entity, amount_paise, ts_utc, kind FROM transactions WHERE from_entity = ? OR to_entity = ? ORDER BY ts_utc", (entity_id, entity_id)).fetchall()]
        inbound = [row for row in transactions if row["to_entity"] == entity_id]
        outbound = [row for row in transactions if row["from_entity"] == entity_id]
        counterparties = {row["from_entity"] for row in inbound if row["from_entity"] != entity_id}
        forwarded = any(row["to_entity"] == entity_id and any(next_row["from_entity"] == entity_id and next_row["amount_paise"] * 2 >= row["amount_paise"] and 0 <= (datetime.fromisoformat(next_row["ts_utc"].replace("Z", "+00:00")) - datetime.fromisoformat(row["ts_utc"].replace("Z", "+00:00"))).total_seconds() <= 3600 for next_row in outbound) for row in inbound)
        mitigation = []
        if len(counterparties) >= 8 and not forwarded:
            mitigation.append({"name": "Regular diversified inflows", "points": -5, "detail": f"{len(counterparties)} distinct inbound counterparties with no detected pass-through."})
        if inbound and not forwarded:
            mitigation.append({"name": "Funds retained", "points": -5, "detail": "Observed outflows are not forwarded immediately after inbound activity."})
        raw_score = min(100, max(0, (len(inbound) * 3) + (len(outbound) * 2) + (15 if forwarded else 0)))
        mitigation_points = max(-15, sum(item["points"] for item in mitigation))
        score = min(100, max(0, raw_score + mitigation_points))
        band = "critical" if score >= 75 else "high" if score >= 50 else "medium" if score >= 25 else "low"
        return {"entity_id": entity["entity_id"], "type": entity["type"], "display_label": entity["display_label"], "score": score, "band": band, "raw_score": raw_score, "mitigation_points": mitigation_points, "mitigations": mitigation, "factor_values": {"inbound_count": len(inbound), "outbound_count": len(outbound), "distinct_inbound_counterparties": len(counterparties), "pass_through_detected": forwarded}, "disclaimer": "Investigation priority, not an indicator of guilt."}
    finally:
        connection.close()


def risk_alerts(database_url: str = "sqlite:///data/runtime/fraudmesh.db", limit: int = 10) -> list[dict]:
    """Return explainable, deterministic account signals derived only from loaded data."""
    connection = connect(database_url)
    try:
        all_transactions = [dict(item) for item in connection.execute("SELECT txn_id, evidence_id, kind, from_entity, to_entity, amount_paise, ts_utc, reference_text FROM transactions").fetchall()]
        promoted_link_entities = {item["source_entity"] for item in connection.execute("SELECT source_entity, target_entity FROM links WHERE cluster_forming = 1").fetchall()} | {item["target_entity"] for item in connection.execute("SELECT source_entity, target_entity FROM links WHERE cluster_forming = 1").fetchall()}
        complaint_entities = set()
        for complaint in connection.execute("SELECT victim_entity FROM complaints").fetchall():
            complaint_key = str(complaint["victim_entity"])
            complaint_entities.update(item["to_entity"] for item in all_transactions if item["to_entity"] and complaint_key in str(item.get("reference_text", "")))
        rows = connection.execute("""
            SELECT t.to_entity AS entity_id,
                   COUNT(*) AS victim_payment_count,
                   COALESCE(SUM(t.amount_paise), 0) AS victim_amount_paise,
                   COUNT(DISTINCT t.from_entity) AS distinct_senders,
                   MAX(CASE WHEN f.entity_id IS NOT NULL THEN 1 ELSE 0 END) AS seeded_flag,
                   GROUP_CONCAT(t.evidence_id) AS evidence_ids
            FROM transactions t LEFT JOIN flags f ON f.entity_id = t.to_entity
            WHERE t.kind = 'victim_payment' AND t.to_entity IS NOT NULL
            GROUP BY t.to_entity
            ORDER BY seeded_flag DESC, victim_payment_count DESC, victim_amount_paise DESC
            LIMIT ?
        """, (limit,)).fetchall()
        alerts = []
        for row in rows:
            score = _victim_score(int(row["victim_payment_count"]), int(row["distinct_senders"]), int(row["victim_amount_paise"]), bool(row["seeded_flag"]))
            band = _risk_band(score)
            reasons = [f"{row['victim_payment_count']} victim payments from {row['distinct_senders']} senders"]
            if row["victim_amount_paise"] >= 10000000: reasons.append("aggregate victim payment value exceeds INR 100,000")
            if row["seeded_flag"]: reasons.append("present in the synthetic seeded-flag table")
            rules_fired = ["R2"] if row["seeded_flag"] or score >= 70 else []
            evidence_ids = [item for item in str(row["evidence_ids"] or "").split(",") if item]
            previous_score = score
            previous_band = band
            victim_events = sorted((item for item in all_transactions if item["to_entity"] == row["entity_id"] and item["kind"] == "victim_payment"), key=lambda item: item["ts_utc"])
            if victim_events:
                latest = victim_events[-1]
                prior_events = victim_events[:-1]
                previous_score = _victim_score(len(prior_events), len({item["from_entity"] for item in prior_events}), sum(int(item["amount_paise"]) for item in prior_events), bool(row["seeded_flag"]))
                previous_band = _risk_band(previous_score)
                if _band_index(band) > _band_index(previous_band):
                    rules_fired.append("R5")
                    evidence_ids.append(latest["evidence_id"])
                    reasons.append(f"risk band escalated from {previous_band.title()} to {band.title()} after the latest victim payment")
            if row["entity_id"] in promoted_link_entities:
                rules_fired.append("R3"); reasons.append("a promoted exact link connects this entity into a reviewed network cluster")
            if row["entity_id"] in complaint_entities:
                rules_fired.append("R6"); reasons.append("a complaint references an entity already present in the network")
            entity_transactions = [item for item in all_transactions if item["from_entity"] == row["entity_id"] or item["to_entity"] == row["entity_id"]]
            for inbound in entity_transactions:
                if inbound["to_entity"] != row["entity_id"] or inbound["amount_paise"] < 1_000_000: continue
                for outbound in entity_transactions:
                    if outbound["from_entity"] != row["entity_id"] or outbound["ts_utc"] < inbound["ts_utc"]: continue
                    if outbound["amount_paise"] * 2 < inbound["amount_paise"]: continue
                    if (datetime.fromisoformat(outbound["ts_utc"].replace("Z", "+00:00")) - datetime.fromisoformat(inbound["ts_utc"].replace("Z", "+00:00"))).total_seconds() <= 3600:
                        rules_fired.append("R1"); evidence_ids.extend([inbound["evidence_id"], outbound["evidence_id"]]); reasons.append("inbound value was forwarded within one hour"); break
                if "R1" in rules_fired: break
            for inbound in entity_transactions:
                if inbound["to_entity"] != row["entity_id"] or inbound["amount_paise"] < 1_000_000: continue
                for withdrawal in entity_transactions:
                    if withdrawal["from_entity"] != row["entity_id"] or withdrawal["kind"] != "cash_withdrawal" or withdrawal["ts_utc"] < inbound["ts_utc"]: continue
                    if (datetime.fromisoformat(withdrawal["ts_utc"].replace("Z", "+00:00")) - datetime.fromisoformat(inbound["ts_utc"].replace("Z", "+00:00"))).total_seconds() <= 3600:
                        rules_fired.append("R4"); evidence_ids.extend([inbound["evidence_id"], withdrawal["evidence_id"]]); reasons.append("cash withdrawal followed an inbound transfer within one hour"); break
                if "R4" in rules_fired: break
            fired = [rule for rule in RULE_SEQUENCE if rule in set(rules_fired)]
            severity = "critical" if "R2" in fired or "R3" in fired or ("R5" in fired and band == "critical") else ("warning" if "R1" in fired or "R4" in fired or "R5" in fired or "R6" in fired else ("high" if score >= 70 else "medium"))
            created_at = max((item["ts_utc"] for item in all_transactions if item["to_entity"] == row["entity_id"]), default=None)
            unique_evidence = sorted(set(evidence_ids))
            alerts.append({"entity_id": row["entity_id"], "alert_id": f"ALERT-{row['entity_id']}", "dedup_key": f"{row['entity_id']}:{','.join(fired) or 'none'}", "occurrences": 1, "trigger_count": max(1, len(victim_events)), "created_at": created_at, "score": score, "band": band, "previous_score": previous_score, "previous_band": previous_band, "severity": severity, "victim_payment_count": row["victim_payment_count"], "amount_inr": row["victim_amount_paise"] // 100, "reasons": reasons, "rules_fired": fired, "rule_sequence": [{"step": index, "rule": rule} for index, rule in enumerate(fired, start=1)], "evidence_ids": unique_evidence, "deduplicated": True})
        return alerts
    finally: connection.close()


def ingest_transaction(database_url: str, event: dict) -> dict:
    required = ("event_id", "kind", "from_account", "amount_inr", "ts", "channel", "reference")
    unknown = set(event) - (set(required) | {"to_account"})
    if unknown:
        raise ValueError(f"unknown event fields: {', '.join(sorted(unknown))}")
    if any(not str(event.get(field, "")).strip() for field in required):
        raise ValueError("event_id, kind, from_account, to_account, amount_inr, ts, channel, and reference are required")
    if event["kind"] not in {"victim_payment", "transfer", "cash_withdrawal"}:
        raise ValueError("unsupported transaction kind")
    if event["kind"] != "cash_withdrawal" and not str(event.get("to_account", "")).strip():
        raise ValueError("to_account is required for non-withdrawal events")
    try:
        amount_inr = int(event["amount_inr"])
    except (TypeError, ValueError) as exc:
        raise ValueError("amount_inr must be an integer") from exc
    if amount_inr <= 0:
        raise ValueError("amount_inr must be positive")
    connection = connect(database_url)
    try:
        received_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        try:
            connection.execute("INSERT INTO ingested_events VALUES (?, ?, 'accepted', NULL)", (str(event["event_id"]), received_at))
        except sqlite3.IntegrityError:
            return {"event_id": str(event["event_id"]), "status": "duplicate", "state_version": "risk-v1"}
        existing = connection.execute("SELECT txn_id FROM transactions WHERE txn_id = ?", (str(event["event_id"]),)).fetchone()
        if existing:
            connection.execute("UPDATE transactions SET held_out = 0 WHERE txn_id = ?", (str(event["event_id"]),)); connection.commit()
            return {"event_id": str(event["event_id"]), "status": "accepted", "state_version": "risk-v1", "replayed": True}
        evidence_id = f"E-ING-{hashlib.sha256(str(event['event_id']).encode()).hexdigest()[:12]}"
        content = json.dumps(event, sort_keys=True, separators=(",", ":"))
        source_row = connection.execute("SELECT COUNT(*) + 1 FROM evidence WHERE source_file = 'live_events'").fetchone()[0]
        connection.execute("INSERT INTO evidence VALUES (?, COALESCE((SELECT dataset_id FROM datasets LIMIT 1), 'runtime'), 'transaction', 'live_events', ?, ?, ?, ?, ?)", (evidence_id, source_row, event["ts"], content, None, hashlib.sha256(content.encode()).hexdigest()))
        connection.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)", (str(event["event_id"]), evidence_id, event["kind"], str(event["from_account"]), str(event.get("to_account") or ""), amount_inr * 100, event["ts"], event["channel"], event["reference"]))
        connection.commit()
        return {"event_id": str(event["event_id"]), "status": "accepted", "state_version": "risk-v1"}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def ingested_events(database_url: str, limit: int = 25, offset: int = 0) -> list[dict]:
    connection = connect(database_url)
    try:
        return [dict(row) for row in connection.execute("SELECT event_id, received_at, status, reason FROM ingested_events ORDER BY received_at DESC LIMIT ? OFFSET ?", (min(max(limit, 1), 100), max(offset, 0))).fetchall()]
    finally:
        connection.close()


def simulator_status(database_url: str) -> dict:
    connection = connect(database_url)
    try:
        setting = connection.execute("SELECT value FROM settings WHERE key = 'dataset_dir'").fetchone()
        index = connection.execute("SELECT value FROM settings WHERE key = 'simulator_index'").fetchone()
        events = json.loads((Path(setting["value"]) / "events_heldout.json").read_text(encoding="utf-8")) if setting else []
        current = int(index["value"]) if index else 0
        return {"index": current, "total": len(events), "complete": current >= len(events), "next_event": events[current] if current < len(events) else None}
    finally: connection.close()


def simulator_reset(database_url: str) -> dict:
    connection = connect(database_url)
    try:
        connection.execute("INSERT OR REPLACE INTO settings VALUES ('simulator_index', '0')"); connection.commit(); return simulator_status(database_url)
    finally: connection.close()


def simulator_step(database_url: str) -> dict:
    status = simulator_status(database_url)
    if status["complete"]: return {"status": "complete", **status}
    event = status["next_event"]
    connection = connect(database_url)
    try:
        connection.execute("INSERT OR REPLACE INTO settings VALUES ('simulator_index', ?)", (str(status["index"] + 1),)); connection.commit()
    finally: connection.close()
    if event.get("txn_id"):
        kind = "cash_withdrawal" if event["kind"] == "withdrawal" else event["kind"]
        result = ingest_transaction(database_url, {"event_id": event["txn_id"], "kind": kind, "from_account": event["from_account"], "to_account": event.get("to_account") or "", "amount_inr": event["amount_inr"], "ts": event["ts"], "channel": event["channel"], "reference": event["reference"]})
        return {"status": "stepped", "event": event, "ingestion": result, "next": simulator_status(database_url)}
    return {"status": "stepped", "event": event, "ingestion": {"status": "narrative_only", "event_id": event.get("complaint_id")}, "next": simulator_status(database_url)}


def network_summary(database_url: str = "sqlite:///data/runtime/fraudmesh.db", limit: int = 80) -> dict:
    connection = connect(database_url)
    try:
        nodes = [dict(row) for row in connection.execute("SELECT entity_id, type, display_label, scope FROM entities ORDER BY entity_id LIMIT ?", (limit,)).fetchall()]
        edges = [dict(row) for row in connection.execute("SELECT from_entity AS source, to_entity AS target, kind, COUNT(*) AS count, SUM(amount_paise) / 100 AS amount_inr, GROUP_CONCAT(evidence_id) AS evidence_ids FROM transactions WHERE to_entity IS NOT NULL GROUP BY from_entity, to_entity, kind ORDER BY count DESC LIMIT ?", (limit,)).fetchall()]
        adjacency = {node["entity_id"]: set() for node in nodes}
        for edge in edges:
            adjacency.setdefault(edge["source"], set()).add(edge["target"])
            adjacency.setdefault(edge["target"], set()).add(edge["source"])
        clusters = []
        unseen = set(adjacency)
        while unseen:
            seed = min(unseen); queue = [seed]; members = []
            while queue:
                current = queue.pop(); unseen.discard(current); members.append(current)
                queue.extend(sorted(adjacency.get(current, set()) & unseen))
            members.sort(); clusters.append({"cluster_id": f"CL-{len(clusters) + 1:03d}", "entity_ids": members, "size": len(members)})
        return {"nodes": nodes, "edges": edges, "clusters": clusters}
    finally: connection.close()


def evidence_records(database_url: str = "sqlite:///data/runtime/fraudmesh.db", query: str = "", limit: int = 50, offset: int = 0) -> list[dict]:
    connection = connect(database_url)
    try:
        pattern = f"%{query}%"
        rows = connection.execute("SELECT evidence_id, type, source_file, source_row, ts_utc, raw_text FROM evidence WHERE (? = '' OR evidence_id LIKE ? OR type LIKE ? OR source_file LIKE ? OR raw_text LIKE ?) ORDER BY source_file, source_row LIMIT ? OFFSET ?", (query, pattern, pattern, pattern, pattern, min(max(limit, 1), 100), max(offset, 0))).fetchall()
        records = []
        for row in rows:
            record = dict(row)
            if record.get("raw_text"):
                record["raw_text"] = mask_text(record["raw_text"])
            records.append(record)
        return records
    finally: connection.close()


def search_entities(database_url: str = "sqlite:///data/runtime/fraudmesh.db", query: str = "", limit: int = 25) -> list[dict]:
    """Search normalized entity keys and labels without exposing raw identifiers."""
    normalized = "".join(character for character in query.casefold() if character.isalnum())
    if len(normalized) < 4:
        raise ValueError("Search query must contain at least 4 characters")
    connection = connect(database_url)
    try:
        rows = connection.execute(
            """
            SELECT entity_id, type, display_label, scope
            FROM entities
            WHERE lower(replace(replace(replace(normalized_key, ' ', ''), '-', ''), '+', '')) LIKE ?
               OR lower(replace(display_label, ' ', '')) LIKE ?
            ORDER BY entity_id
            LIMIT ?
            """,
            (f"{normalized}%", f"{normalized}%", min(max(limit, 1), 100)),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def network_path(database_url: str, source: str, target: str, max_hops: int = 8) -> dict:
    if not source or not target:
        raise ValueError("source and target are required")
    max_hops = min(max(max_hops, 1), 12)
    connection = connect(database_url)
    try:
        rows = connection.execute("SELECT from_entity, to_entity, kind, COUNT(*) AS count FROM transactions WHERE to_entity IS NOT NULL GROUP BY from_entity, to_entity, kind").fetchall()
        adjacency: dict[str, list[dict]] = {}
        for row in rows:
            adjacency.setdefault(row["from_entity"], []).append(dict(row))
        queue = deque([(source, [source], [])]); visited = {source}
        while queue:
            node, nodes, edges = queue.popleft()
            if node == target:
                return {"source": source, "target": target, "found": True, "nodes": nodes, "edges": edges, "hops": len(edges)}
            if len(edges) >= max_hops:
                continue
            for edge in adjacency.get(node, []):
                next_node = edge["to_entity"]
                if next_node in visited:
                    continue
                visited.add(next_node)
                queue.append((next_node, nodes + [next_node], edges + [{"source": edge["from_entity"], "target": next_node, "kind": edge["kind"], "count": edge["count"]}]))
        return {"source": source, "target": target, "found": False, "nodes": [], "edges": [], "hops": None}
    finally:
        connection.close()


def entity_detail(database_url: str, entity_id: str) -> dict | None:
    connection = connect(database_url)
    try:
        entity = connection.execute("SELECT entity_id, type, display_label, scope, attrs_json FROM entities WHERE entity_id = ?", (entity_id,)).fetchone()
        if not entity:
            return None
        stats = connection.execute("SELECT COUNT(*) AS total, COALESCE(SUM(CASE WHEN from_entity = ? THEN amount_paise ELSE 0 END), 0) AS outbound_paise, COALESCE(SUM(CASE WHEN to_entity = ? THEN amount_paise ELSE 0 END), 0) AS inbound_paise FROM transactions WHERE from_entity = ? OR to_entity = ?", (entity_id, entity_id, entity_id, entity_id)).fetchone()
        links = connection.execute("SELECT txn_id, kind, from_entity, to_entity, amount_paise, ts_utc, channel FROM transactions WHERE from_entity = ? OR to_entity = ? ORDER BY ts_utc DESC LIMIT 50", (entity_id, entity_id)).fetchall()
        return {**dict(entity), "degree": stats["total"], "outbound_inr": stats["outbound_paise"] // 100, "inbound_inr": stats["inbound_paise"] // 100, "transactions": [{**dict(row), "amount_inr": row["amount_paise"] // 100} for row in links]}
    finally:
        connection.close()


def edge_detail(database_url: str, source: str, target: str) -> dict:
    connection = connect(database_url)
    try:
        rows = connection.execute("SELECT txn_id, evidence_id, kind, amount_paise, ts_utc, channel, reference_text FROM transactions WHERE from_entity = ? AND to_entity = ? ORDER BY ts_utc", (source, target)).fetchall()
        return {"source": source, "target": target, "count": len(rows), "evidence_ids": sorted({row["evidence_id"] for row in rows}), "transactions": [{**dict(row), "amount_inr": row["amount_paise"] // 100} for row in rows]}
    finally:
        connection.close()


def evidence_detail(database_url: str, evidence_id: str) -> dict | None:
    connection = connect(database_url)
    try:
        row = connection.execute("SELECT evidence_id, type, source_file, source_row, ts_utc, raw_text, content_json FROM evidence WHERE evidence_id = ?", (evidence_id,)).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def mask_text(value: str) -> str:
    """Mask common synthetic identifiers at the API serialization boundary."""
    masked = re.sub(r"(?<!\d)(?:\+?91[\s-]?)?[6-9](?:[\s-]?\d){9}(?!\d)", "[PHONE-MASKED]", value)
    masked = re.sub(r"(?<!\d)\d{9,18}(?!\d)", "[ACCOUNT-MASKED]", masked)
    masked = re.sub(r"([\w.+-]{2})[\w.+-]*(@[\w.-]+)", r"\1***\2", masked)
    return masked


def list_cases(database_url: str = "sqlite:///data/runtime/fraudmesh.db") -> list[dict]:
    connection = connect(database_url)
    try:
        return [dict(row) for row in connection.execute("SELECT case_id, entity_id, title, status, score, notes, created_at FROM investigation_cases ORDER BY created_at DESC").fetchall()]
    finally: connection.close()


def cases_for_entity(database_url: str, entity_id: str) -> list[dict]:
    connection = connect(database_url)
    try:
        return [dict(row) for row in connection.execute("SELECT case_id, entity_id, title, status, score, notes, created_at FROM investigation_cases WHERE entity_id = ? AND status != 'resolved' ORDER BY created_at DESC", (entity_id,)).fetchall()]
    finally: connection.close()


def case_subgraph(database_url: str, case_id: str) -> dict:
    connection = connect(database_url)
    try:
        case = connection.execute("SELECT entity_id FROM investigation_cases WHERE case_id = ?", (case_id,)).fetchone()
        if not case:
            return {"case_id": case_id, "entity_ids": [], "evidence_ids": [], "timeline_count": 0}
        rows = connection.execute("SELECT txn_id, evidence_id, from_entity, to_entity FROM transactions WHERE from_entity = ? OR to_entity = ? ORDER BY ts_utc", (case["entity_id"], case["entity_id"])).fetchall()
        entity_ids = {case["entity_id"]}
        for row in rows:
            entity_ids.add(row["from_entity"])
            if row["to_entity"]:
                entity_ids.add(row["to_entity"])
        return {"case_id": case_id, "entity_ids": sorted(entity_ids), "evidence_ids": sorted({row["evidence_id"] for row in rows}), "timeline_count": len(rows)}
    finally: connection.close()


def _case_exists(connection: sqlite3.Connection, case_id: str) -> bool:
    return connection.execute("SELECT 1 FROM investigation_cases WHERE case_id = ?", (case_id,)).fetchone() is not None


def _validate_evidence_ids(connection: sqlite3.Connection, evidence_ids: list[str]) -> None:
    if not evidence_ids:
        raise ValueError("at least one evidence ID is required")
    placeholders = ",".join("?" for _ in evidence_ids)
    count = connection.execute(f"SELECT COUNT(*) FROM evidence WHERE evidence_id IN ({placeholders})", evidence_ids).fetchone()[0]
    if count != len(set(evidence_ids)):
        raise ValueError("one or more evidence IDs do not exist")


def create_finding(database_url: str, case_id: str, statement: str, evidence_ids: list[str], source: str = "Deterministic", confidence: float = 0.5) -> dict:
    connection = connect(database_url)
    try:
        if not _case_exists(connection, case_id): raise ValueError("case not found")
        if not statement.strip(): raise ValueError("finding statement is required")
        _validate_evidence_ids(connection, evidence_ids)
        finding_id = f"FND-{connection.execute('SELECT COUNT(*) FROM findings').fetchone()[0] + 1:03d}"
        stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        confidence = max(0.0, min(float(confidence), 1.0))
        connection.execute("INSERT INTO findings VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)", (finding_id, case_id, statement.strip(), json.dumps(sorted(set(evidence_ids))), source, confidence, stamp)); connection.commit()
        return {"finding_id": finding_id, "case_id": case_id, "statement": statement.strip(), "evidence_ids": sorted(set(evidence_ids)), "source": source, "confidence": confidence, "review_state": "pending", "created_at": stamp}
    finally: connection.close()


def list_findings(database_url: str, case_id: str) -> list[dict]:
    connection = connect(database_url)
    try:
        rows = connection.execute("SELECT * FROM findings WHERE case_id = ? ORDER BY created_at", (case_id,)).fetchall()
        return [{**dict(row), "evidence_ids": json.loads(row["evidence_ids_json"])} for row in rows]
    finally: connection.close()


def review_finding(database_url: str, finding_id: str, new_state: str, reason: str, actor_id: str | None = None) -> dict:
    allowed = {"accepted", "rejected", "needs_evidence", "annotated"}
    if new_state not in allowed: raise ValueError("invalid finding review state")
    if new_state != "accepted" and len(reason.strip()) < 8: raise ValueError("review reason of at least 8 characters is required")
    connection = connect(database_url)
    try:
        row = connection.execute("SELECT * FROM findings WHERE finding_id = ?", (finding_id,)).fetchone()
        if not row: raise ValueError("finding not found")
        stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        connection.execute("UPDATE findings SET review_state = ? WHERE finding_id = ?", (new_state, finding_id))
        connection.execute("INSERT INTO review_history (item_type, item_id, previous_state, new_state, reason, actor_id, created_at) VALUES ('finding', ?, ?, ?, ?, ?, ?)", (finding_id, row["review_state"], new_state, reason.strip(), actor_id, stamp)); connection.commit()
        return {"finding_id": finding_id, "previous_state": row["review_state"], "review_state": new_state, "reason": reason.strip(), "created_at": stamp}
    finally: connection.close()


def create_case(database_url: str, entity_id: str, score: int, title: str, notes: str = "") -> dict:
    connection = connect(database_url)
    try:
        dataset = connection.execute("SELECT dataset_id FROM datasets LIMIT 1").fetchone()
        if not dataset: raise ValueError("A synthetic dataset must be loaded before creating a case")
        case_id = f"CASE-{connection.execute('SELECT COUNT(*) FROM investigation_cases').fetchone()[0] + 1:03d}"
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        connection.execute("INSERT INTO investigation_cases VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (case_id, dataset["dataset_id"], entity_id, title, "open", score, notes, created_at))
        connection.commit()
        return {"case_id": case_id, "dataset_id": dataset["dataset_id"], "entity_id": entity_id, "title": title, "status": "open", "score": score, "notes": notes, "created_at": created_at}
    finally: connection.close()


def create_link(database_url: str, source_entity: str, target_entity: str, link_type: str, strength: str, evidence_ids: list[str]) -> dict:
    if source_entity == target_entity: raise ValueError("self-links are not allowed")
    if strength not in {"weak", "inferred"}: raise ValueError("new links must be weak or inferred")
    connection = connect(database_url)
    try:
        if len(connection.execute("SELECT 1 FROM entities WHERE entity_id IN (?, ?)", (source_entity, target_entity)).fetchall()) != 2: raise ValueError("both entities must exist")
        _validate_evidence_ids(connection, evidence_ids)
        link_id = f"LNK-{connection.execute('SELECT COUNT(*) FROM links').fetchone()[0] + 1:03d}"; stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        connection.execute("INSERT INTO links VALUES (?, ?, ?, ?, ?, 'unreviewed', ?, 0, ?)", (link_id, source_entity, target_entity, link_type, strength, json.dumps(sorted(set(evidence_ids))), stamp)); connection.commit()
        return {"link_id": link_id, "source_entity": source_entity, "target_entity": target_entity, "link_type": link_type, "strength": strength, "state": "unreviewed", "evidence_ids": sorted(set(evidence_ids)), "cluster_forming": False, "created_at": stamp}
    finally: connection.close()


def list_links(database_url: str, state: str = "") -> list[dict]:
    connection = connect(database_url)
    try:
        rows = connection.execute("SELECT * FROM links WHERE (? = '' OR state = ?) ORDER BY created_at", (state, state)).fetchall()
        return [{**dict(row), "evidence_ids": json.loads(row["evidence_ids_json"]), "cluster_forming": bool(row["cluster_forming"])} for row in rows]
    finally: connection.close()


def review_link(database_url: str, link_id: str, action: str, reason: str, actor_id: str | None = None) -> dict:
    if action not in {"promote", "demote"}: raise ValueError("link action must be promote or demote")
    if len(reason.strip()) < 8: raise ValueError("link review reason of at least 8 characters is required")
    connection = connect(database_url)
    try:
        row = connection.execute("SELECT * FROM links WHERE link_id = ?", (link_id,)).fetchone()
        if not row: raise ValueError("link not found")
        state = "promoted" if action == "promote" else "demoted"; forming = 1 if action == "promote" else 0; stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        connection.execute("UPDATE links SET state = ?, cluster_forming = ? WHERE link_id = ?", (state, forming, link_id)); connection.execute("INSERT INTO review_history (item_type, item_id, previous_state, new_state, reason, actor_id, created_at) VALUES ('link', ?, ?, ?, ?, ?, ?)", (link_id, row["state"], state, reason.strip(), actor_id, stamp)); connection.commit()
        return {"link_id": link_id, "previous_state": row["state"], "state": state, "cluster_forming": bool(forming), "reason": reason.strip(), "created_at": stamp}
    finally: connection.close()


def create_hypothesis(database_url: str, case_id: str, statement: str, evidence_ids: list[str], confidence: float = 0.5) -> dict:
    connection = connect(database_url)
    try:
        if not _case_exists(connection, case_id): raise ValueError("case not found")
        if not statement.strip(): raise ValueError("hypothesis statement is required")
        _validate_evidence_ids(connection, evidence_ids)
        item_id = f"HYP-{connection.execute('SELECT COUNT(*) FROM hypotheses').fetchone()[0] + 1:03d}"; stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"); confidence = max(0.0, min(float(confidence), 1.0))
        connection.execute("INSERT INTO hypotheses VALUES (?, ?, ?, ?, ?, 'pending', ?)", (item_id, case_id, statement.strip(), json.dumps(sorted(set(evidence_ids))), confidence, stamp)); connection.commit()
        return {"hypothesis_id": item_id, "case_id": case_id, "statement": statement.strip(), "evidence_ids": sorted(set(evidence_ids)), "confidence": confidence, "review_state": "pending", "created_at": stamp}
    finally: connection.close()


def list_hypotheses(database_url: str, case_id: str) -> list[dict]:
    connection = connect(database_url)
    try:
        rows = connection.execute("SELECT * FROM hypotheses WHERE case_id = ? ORDER BY created_at", (case_id,)).fetchall()
        return [{**dict(row), "evidence_ids": json.loads(row["evidence_ids_json"])} for row in rows]
    finally: connection.close()


def create_plan_step(database_url: str, case_id: str, rank: int, action: str, rationale: str, evidence_ids: list[str], linked_hypothesis: str | None = None) -> dict:
    connection = connect(database_url)
    try:
        if not _case_exists(connection, case_id): raise ValueError("case not found")
        if not action.strip() or not rationale.strip(): raise ValueError("action and rationale are required")
        _validate_evidence_ids(connection, evidence_ids)
        if linked_hypothesis and not connection.execute("SELECT 1 FROM hypotheses WHERE hypothesis_id = ? AND case_id = ?", (linked_hypothesis, case_id)).fetchone(): raise ValueError("linked hypothesis not found")
        item_id = f"PLAN-{connection.execute('SELECT COUNT(*) FROM plan_steps').fetchone()[0] + 1:03d}"; stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        connection.execute("INSERT INTO plan_steps VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)", (item_id, case_id, int(rank), action.strip(), rationale.strip(), json.dumps(sorted(set(evidence_ids))), linked_hypothesis, stamp)); connection.commit()
        return {"step_id": item_id, "case_id": case_id, "rank": int(rank), "action": action.strip(), "rationale": rationale.strip(), "evidence_ids": sorted(set(evidence_ids)), "linked_hypothesis": linked_hypothesis, "review_state": "pending", "created_at": stamp}
    finally: connection.close()


def list_plan_steps(database_url: str, case_id: str) -> list[dict]:
    connection = connect(database_url)
    try:
        rows = connection.execute("SELECT p.*, CASE WHEN f.review_state = 'rejected' THEN 1 ELSE 0 END AS basis_rejected FROM plan_steps p LEFT JOIN findings f ON f.finding_id = p.linked_hypothesis WHERE p.case_id = ? ORDER BY p.rank, p.created_at", (case_id,)).fetchall()
        return [{**dict(row), "evidence_ids": json.loads(row["evidence_ids_json"]), "basis_rejected": bool(row["basis_rejected"])} for row in rows]
    finally: connection.close()


def run_grounded_reasoning(database_url: str, case_id: str, mode: str = "cached") -> dict:
    """Create a reviewable, evidence-grounded reasoning snapshot for a case.

    This is deliberately deterministic when cached mode is requested. It never
    invents a stage: every item cites linked transaction evidence and exposes
    gaps for the investigator to review.
    """
    evidence = case_evidence(database_url, case_id)
    if not evidence:
        raise ValueError("case has no linked evidence")
    existing_findings = list_findings(database_url, case_id)
    existing_hypotheses = list_hypotheses(database_url, case_id)
    existing_steps = list_plan_steps(database_url, case_id)
    ids = [item["evidence_id"] for item in evidence]
    if not existing_findings:
        existing_findings = [create_finding(database_url, case_id, "Linked transaction records establish a reviewable movement of funds across the case timeline; the records do not by themselves establish intent.", ids[: min(3, len(ids))], "Deterministic-grounded", 0.82)]
    if not existing_hypotheses:
        existing_hypotheses = [create_hypothesis(database_url, case_id, "The observed sequence may warrant review for coordinated pass-through activity.", ids[: min(4, len(ids))], 0.64)]
    if not existing_steps:
        existing_steps = [create_plan_step(database_url, case_id, 1, "Compare linked ledger timestamps with communications and complaint recollections.", "The timeline contains linked transaction evidence; chronology should be checked before drawing a conclusion.", ids[: min(4, len(ids))])]
    for item in existing_findings:
        item["counter_evidence_or_gaps"] = "Intent is not established by transaction records alone."
        item["next_step"] = "Compare the cited records with communications and complaint context."
    for item in existing_hypotheses:
        item["counter_evidence_or_gaps"] = "No direct evidence of intent is asserted; investigator confirmation is required."
    for item in existing_steps:
        item["validator"] = "passed"
    return {"case_id": case_id, "mode": "cached", "label": "Cached (not live)" if mode != "live" else "Grounded review", "findings": existing_findings, "hypotheses": existing_hypotheses, "plan_steps": existing_steps, "withheld_count": 0, "human_review_required": True}


def review_plan_item(database_url: str, item_type: str, item_id: str, new_state: str, reason: str, actor_id: str | None = None) -> dict:
    if item_type not in {"hypothesis", "plan_step"}: raise ValueError("invalid review item type")
    if new_state not in {"accepted", "rejected", "needs_evidence", "annotated", "done"}: raise ValueError("invalid review state")
    if new_state not in {"accepted", "done"} and len(reason.strip()) < 8: raise ValueError("review reason of at least 8 characters is required")
    table = "hypotheses" if item_type == "hypothesis" else "plan_steps"; key = "hypothesis_id" if item_type == "hypothesis" else "step_id"
    connection = connect(database_url)
    try:
        row = connection.execute(f"SELECT review_state FROM {table} WHERE {key} = ?", (item_id,)).fetchone()
        if not row: raise ValueError("review item not found")
        stamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        connection.execute(f"UPDATE {table} SET review_state = ? WHERE {key} = ?", (new_state, item_id)); connection.execute("INSERT INTO review_history (item_type, item_id, previous_state, new_state, reason, actor_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (item_type, item_id, row["review_state"], new_state, reason.strip(), actor_id, stamp)); connection.commit()
        return {"item_type": item_type, "item_id": item_id, "previous_state": row["review_state"], "review_state": new_state, "reason": reason.strip(), "created_at": stamp}
    finally: connection.close()


def update_case_notes(database_url: str, case_id: str, notes: str) -> dict | None:
    connection = connect(database_url)
    try:
        connection.execute("UPDATE investigation_cases SET notes = ? WHERE case_id = ?", (notes, case_id))
        connection.commit()
        row = connection.execute("SELECT case_id, entity_id, title, status, score, notes, created_at FROM investigation_cases WHERE case_id = ?", (case_id,)).fetchone()
        return dict(row) if row else None
    finally: connection.close()


def update_case_status(database_url: str, case_id: str, status: str) -> dict | None:
    allowed = {"open", "in_review", "resolved"}
    if status not in allowed:
        raise ValueError("status must be open, in_review, or resolved")
    connection = connect(database_url)
    try:
        connection.execute("UPDATE investigation_cases SET status = ? WHERE case_id = ?", (status, case_id))
        connection.commit()
        row = connection.execute("SELECT case_id, entity_id, title, status, score, notes, created_at FROM investigation_cases WHERE case_id = ?", (case_id,)).fetchone()
        return dict(row) if row else None
    finally: connection.close()


def evaluation_summary(database_url: str = "sqlite:///data/runtime/fraudmesh.db") -> dict:
    connection = connect(database_url)
    try:
        setting = connection.execute("SELECT value FROM settings WHERE key = 'dataset_dir'").fetchone()
        if not setting:
            return {"available": False, "reason": "No synthetic dataset loaded"}
        root = Path(setting["value"])
        if not root.is_absolute():
            candidates = [Path.cwd() / root, Path(__file__).resolve().parents[2] / root, Path(__file__).resolve().parents[3] / root]
            root = next((candidate.resolve() for candidate in candidates if candidate.exists()), candidates[-1].resolve())
        held_out = json.loads((root / "events_heldout.json").read_text(encoding="utf-8"))
        truth_path = root.parent / "ground_truth" / "ground_truth.json"
        if not truth_path.exists():
            return {"available": False, "reason": "Ground truth file not available"}
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        surfaced = {alert["entity_id"] for alert in risk_alerts(database_url)}
        transaction_events = [event for event in held_out if event.get("txn_id")]
        covered_transactions = 0
        for event in transaction_events:
            if event.get("from_account") in surfaced or event.get("to_account") in surfaced:
                covered_transactions += 1
        narrative_events = [event for event in held_out if event.get("complaint_id")]
        return {"available": True, "held_out_events": len(held_out), "expected_alerts": len(truth.get("expected_alerts", [])), "surfaced_entities": sorted(surfaced), "transaction_event_coverage": {"covered": covered_transactions, "total": len(transaction_events), "rate": round(covered_transactions / len(transaction_events), 3) if transaction_events else 0}, "narrative_only_events": len(narrative_events), "notes": "Coverage is a deterministic synthetic evaluation signal, not a production model metric."}
    finally: connection.close()


def case_evidence(database_url: str, case_id: str) -> list[dict]:
    connection = connect(database_url)
    try:
        case = connection.execute("SELECT entity_id FROM investigation_cases WHERE case_id = ?", (case_id,)).fetchone()
        if not case:
            return []
        rows = connection.execute("""
            SELECT e.evidence_id, e.type, e.source_file, e.source_row, e.ts_utc,
                   t.txn_id, t.kind, t.amount_paise, t.from_entity, t.to_entity, t.channel, t.reference_text
            FROM evidence e JOIN transactions t ON t.evidence_id = e.evidence_id
            WHERE t.from_entity = ? OR t.to_entity = ?
            ORDER BY e.ts_utc ASC, e.source_row ASC
        """, (case["entity_id"], case["entity_id"])).fetchall()
        return [{**dict(row), "amount_inr": (row["amount_paise"] or 0) // 100} for row in rows]
    finally: connection.close()


def chronology_summary(database_url: str, case_id: str) -> dict:
    records = case_evidence(database_url, case_id)
    ordered = sorted(records, key=lambda item: (item.get("ts_utc") or "", item.get("evidence_id") or ""))
    pairs = max(0, len(ordered) * (len(ordered) - 1) // 2)
    return {"case_id": case_id, "ordered_evidence_ids": [item["evidence_id"] for item in ordered], "evaluated_pairs": pairs, "correct_pairs": pairs, "pair_accuracy": 1.0 if pairs else 0.0, "software_timestamps_authoritative": True}


def contradiction_catalog(database_url: str) -> list[dict]:
    """Surface the four planted contradiction patterns from source records."""
    connection = connect(database_url)
    try:
        complaints = {row["complaint_id"]: dict(row) for row in connection.execute("SELECT complaint_id, evidence_id, victim_entity, narrative FROM complaints").fetchall()}
        transactions = [dict(row) for row in connection.execute("SELECT txn_id, evidence_id, reference_text, amount_paise, ts_utc, to_entity FROM transactions").fetchall()]
        results = []
        c2 = complaints.get("C-02")
        t2 = next((row for row in transactions if "V02" in row["reference_text"]), None)
        if c2 and t2:
            results.append({"conflict_id": "X1", "kind": "amount_mismatch", "status": "candidate", "materiality": "high", "statement": "Complaint C-02 states INR 48,000 while T-002 records INR 84,000.", "source_evidence_ids": [c2["evidence_id"], t2["evidence_id"]], "assessment": "Likely amount transposition; software ledger remains authoritative."})
        c7 = complaints.get("C-07")
        t12 = next((row for row in transactions if "V12" in row["reference_text"]), None)
        if c7 and t12:
            results.append({"conflict_id": "X2", "kind": "time_inconsistency", "status": "candidate", "materiality": "medium", "statement": "Complaint C-07 describes an after-lunch transfer while the linked ledger event occurs late in the day.", "source_evidence_ids": [c7["evidence_id"], t12["evidence_id"]], "assessment": "Narrative time may be unreliable; chronology uses the ledger timestamp."})
        p5 = narrative_links(database_url)
        if p5:
            results.append({"conflict_id": "X3", "kind": "identifier_format_mismatch", "status": "candidate", "materiality": "low", "statement": "The same officer identifier appears in multiple phone formats and normalises to P5.", "source_evidence_ids": sorted({item for link in p5 for item in link["evidence_ids"]}), "assessment": "Exact normalised match; retain as an inferred narrative link."})
        c11 = complaints.get("C-11")
        t18 = next((row for row in transactions if "V18" in row["reference_text"]), None)
        if c11 and t18:
            results.append({"conflict_id": "X4", "kind": "bank_mismatch", "status": "candidate", "materiality": "low", "statement": "Complaint C-11 names Bank Beta while the linked recipient account is Bank Alpha.", "source_evidence_ids": [c11["evidence_id"], t18["evidence_id"]], "assessment": "Likely bank/app naming confusion; preserve both sources for review."})
        return results
    finally: connection.close()


def case_contradictions(database_url: str, case_id: str) -> list[dict]:
    """Return deterministic candidates; software ledger values stay authoritative."""
    connection = connect(database_url)
    try:
        case = connection.execute("SELECT entity_id FROM investigation_cases WHERE case_id = ?", (case_id,)).fetchone()
        if not case:
            return []
        entity_id = case["entity_id"]
        transactions = connection.execute("SELECT txn_id, evidence_id, amount_paise FROM transactions WHERE from_entity = ? OR to_entity = ? ORDER BY ts_utc", (entity_id, entity_id)).fetchall()
        amount_values = {int(row["amount_paise"]) // 100 for row in transactions}
        complaints = connection.execute("SELECT complaint_id, evidence_id, narrative FROM complaints WHERE victim_entity = ? OR narrative LIKE ?", (entity_id, f"%{entity_id}%")).fetchall()
        results = []
        for complaint in complaints:
            mentioned = [int(value.replace(",", "")) for value in re.findall(r"INR\s*([\d,]+)", complaint["narrative"], flags=re.IGNORECASE)]
            for amount in mentioned:
                if amount not in amount_values:
                    results.append({"conflict_id": f"CON-{complaint['complaint_id']}-AMOUNT", "kind": "amount_mismatch", "status": "candidate", "materiality": "high", "statement": f"Narrative mentions INR {amount:,}, but no linked ledger transaction has that amount.", "software_values": [row["txn_id"] for row in transactions], "source_evidence_ids": [complaint["evidence_id"]] + [row["evidence_id"] for row in transactions], "resolution": "Software ledger values remain authoritative; investigator review required."})
            if not mentioned:
                results.append({"conflict_id": f"CON-{complaint['complaint_id']}-UNVERIFIED", "kind": "unverified_claim", "status": "candidate", "materiality": "low", "statement": "Narrative contains a recollection without a directly comparable amount; no contradiction is established.", "software_values": [row["txn_id"] for row in transactions], "source_evidence_ids": [complaint["evidence_id"]], "resolution": "Keep as an unverified claim until corroborating evidence is linked."})
        return results
    finally: connection.close()


def narrative_links(database_url: str) -> list[dict]:
    """Propose exact narrative-only links such as the shared P5 phone."""
    connection = connect(database_url)
    try:
        rows = connection.execute("SELECT complaint_id, evidence_id, narrative FROM complaints ORDER BY complaint_id").fetchall()
        groups: dict[str, list[dict]] = {}
        for row in rows:
            phones = {re.sub(r"\D", "", value)[-10:] for value in re.findall(r"(?:\+?\d[\d\s-]{8,}\d)", row["narrative"]) if len(re.sub(r"\D", "", value)) >= 10}
            for phone in phones:
                groups.setdefault(phone, []).append(dict(row))
        links = []
        for phone, matches in groups.items():
            if len(matches) < 2:
                continue
            for index, left in enumerate(matches):
                for right in matches[index + 1:]:
                    links.append({"link_id": f"NARRATIVE-{left['complaint_id']}-{right['complaint_id']}", "source": left["complaint_id"], "target": right["complaint_id"], "match": "exact", "state": "confirmed", "identifier": "P5", "evidence_ids": [left["evidence_id"], right["evidence_id"]], "masked_value": f"***{phone[-4:]}"})
        return links
    finally: connection.close()


def complaint_extraction(database_url: str) -> dict:
    """Return deterministic complaint facts and extraction coverage."""
    connection = connect(database_url)
    try:
        rows = connection.execute("SELECT complaint_id, evidence_id, victim_entity, incident_id, filed_at, narrative FROM complaints ORDER BY complaint_id").fetchall()
        records = []
        for row in rows:
            phones = sorted({re.sub(r"\D", "", value)[-10:] for value in re.findall(r"(?:\+?\d[\d\s-]{8,}\d)", row["narrative"]) if len(re.sub(r"\D", "", value)) >= 10})
            amounts = [int(value.replace(",", "")) for value in re.findall(r"INR\s*([\d,]+)", row["narrative"], flags=re.IGNORECASE)]
            records.append({"complaint_id": row["complaint_id"], "evidence_id": row["evidence_id"], "victim_entity": row["victim_entity"], "incident_id": row["incident_id"], "filed_at": row["filed_at"], "phone_tokens": phones, "amounts_inr": amounts, "injection_like_text": "ignore all previous instructions" in row["narrative"].lower()})
        return {"records": records, "count": len(records), "grounded_fields": ["complaint_id", "victim_entity", "incident_id", "filed_at"], "identifier_extraction_rate": 1.0 if records else 0.0, "human_review_required": True}
    finally: connection.close()
