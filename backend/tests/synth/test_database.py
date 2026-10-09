import json
import shutil
from pathlib import Path

import pytest

from app.db.database import _risk_band, _victim_score, alert_actions, alert_status, apply_alert_action, case_evidence, case_subgraph, cases_for_entity, chronology_summary, complaint_extraction, contradiction_catalog, create_case, create_finding, create_hypothesis, create_link, create_plan_step, current_summary, entity_detail, evidence_records, evaluation_summary, ingest_transaction, list_cases, list_findings, list_hypotheses, list_links, list_plan_steps, load_dataset, mask_text, narrative_links, network_path, network_summary, review_finding, review_link, review_plan_item, risk_alerts, risk_profile, rollback_alert_action, run_grounded_reasoning, search_entities, simulator_reset, simulator_status, simulator_step, update_case_notes, update_case_status
from app.synth.generate import generate


def test_loader_populates_summary_and_refuses_non_synthetic():
    root = Path.cwd() / "tests" / "_loader_tmp"; shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
    try:
        demo = root / "demo"; generate(out_dir=demo, ground_truth_dir=root / "ground_truth")
        db = root / "fraudmesh.db"
        result = load_dataset(demo, f"sqlite:///{db}")
        summary = current_summary(f"sqlite:///{db}")
        assert result["counts"]["transactions"] == 56
        assert summary["dataset_loaded"] is True
        alerts = risk_alerts(f"sqlite:///{db}")
        assert alerts and alerts[0]["score"] >= alerts[-1]["score"]
        assert all("rules_fired" in alert and "evidence_ids" in alert for alert in alerts)
        assert all(alert["alert_id"].startswith("ALERT-") and alert["occurrences"] == 1 for alert in alerts)
        assert any(alert["rules_fired"] for alert in alerts)
        assert all(alert["band"] in {"low", "medium", "high", "critical"} for alert in alerts)
        assert any("R5" in alert["rules_fired"] and alert["previous_band"] != alert["band"] for alert in alerts)
        assert any("R6" in alert["rules_fired"] for alert in alerts)
        graph = network_summary(f"sqlite:///{db}")
        assert graph["nodes"] and graph["edges"]
        assert graph["clusters"] and all(cluster["cluster_id"].startswith("CL-") for cluster in graph["clusters"])
        edge = graph["edges"][0]
        assert network_path(f"sqlite:///{db}", edge["source"], edge["target"])["found"] is True
        assert entity_detail(f"sqlite:///{db}", edge["source"])["degree"] > 0
        assert len(evidence_records(f"sqlite:///{db}", query="complaint")) == 13
        p5_links = narrative_links(f"sqlite:///{db}")
        assert any(link["identifier"] == "P5" and link["match"] == "exact" for link in p5_links)
        extraction = complaint_extraction(f"sqlite:///{db}")
        assert extraction["count"] == 13 and extraction["identifier_extraction_rate"] >= 0.9
        assert {item["conflict_id"] for item in contradiction_catalog(f"sqlite:///{db}")} == {"X1", "X2", "X3", "X4"}
        created = create_case(f"sqlite:///{db}", "ACC-M3", 100, "Review ACC-M3", "derived synthetic signal")
        assert created["case_id"] == "CASE-001"
        assert list_cases(f"sqlite:///{db}")[0]["status"] == "open"
        assert cases_for_entity(f"sqlite:///{db}", "ACC-M3")[0]["case_id"] == "CASE-001"
        subgraph = case_subgraph(f"sqlite:///{db}", "CASE-001")
        assert "ACC-M3" in subgraph["entity_ids"] and subgraph["timeline_count"] > 0
        updated = update_case_notes(f"sqlite:///{db}", "CASE-001", "investigator review note")
        assert updated and updated["notes"] == "investigator review note"
        status_updated = update_case_status(f"sqlite:///{db}", "CASE-001", "in_review")
        assert status_updated and status_updated["status"] == "in_review"
        finding = create_finding(f"sqlite:///{db}", "CASE-001", "The evidence indicates a potential payment relationship.", ["E-0001"], confidence=0.7)
        assert list_findings(f"sqlite:///{db}", "CASE-001")[0]["review_state"] == "pending"
        with pytest.raises(ValueError, match="reason"):
            review_finding(f"sqlite:///{db}", finding["finding_id"], "rejected", "short")
        assert review_finding(f"sqlite:///{db}", finding["finding_id"], "accepted", "") ["review_state"] == "accepted"
        hypothesis = create_hypothesis(f"sqlite:///{db}", "CASE-001", "The payment flow may indicate a pass-through pattern.", ["E-0001"], 0.6)
        step = create_plan_step(f"sqlite:///{db}", "CASE-001", 1, "Review linked transaction timing", "Clarify chronology from source records", ["E-0001"], hypothesis["hypothesis_id"])
        assert list_hypotheses(f"sqlite:///{db}", "CASE-001")[0]["hypothesis_id"] == hypothesis["hypothesis_id"]
        assert list_plan_steps(f"sqlite:///{db}", "CASE-001")[0]["basis_rejected"] is False
        reasoning = run_grounded_reasoning(f"sqlite:///{db}", "CASE-001", "cached")
        assert reasoning["label"] == "Cached (not live)" and reasoning["findings"] and reasoning["hypotheses"] and reasoning["plan_steps"]
        assert all(item["evidence_ids"] for item in reasoning["findings"])
        assert review_plan_item(f"sqlite:///{db}", "hypothesis", hypothesis["hypothesis_id"], "accepted", "") ["review_state"] == "accepted"
        assert review_plan_item(f"sqlite:///{db}", "plan_step", step["step_id"], "done", "") ["review_state"] == "done"
        link = create_link(f"sqlite:///{db}", "ACC-M3", "ACC-M2", "model_inferred", "inferred", ["E-0001"])
        assert list_links(f"sqlite:///{db}")[0]["cluster_forming"] is False
        assert review_link(f"sqlite:///{db}", link["link_id"], "promote", "Investigator confirmed relationship")["cluster_forming"] is True
        assert review_link(f"sqlite:///{db}", link["link_id"], "demote", "Evidence is insufficient")["cluster_forming"] is False
        review_link(f"sqlite:///{db}", link["link_id"], "promote", "Confirmed by investigator review")
        assert "R3" in next(alert for alert in risk_alerts(f"sqlite:///{db}") if alert["entity_id"] == "ACC-M3")["rules_fired"]
        assert simulator_status(f"sqlite:///{db}")["total"] == 7
        simulator_reset(f"sqlite:///{db}")
        stepped = simulator_step(f"sqlite:///{db}")
        assert stepped["status"] == "stepped" and stepped["ingestion"]["status"] == "accepted"
        assert apply_alert_action(f"sqlite:///{db}", "ACC-M3", "acknowledge")["action"] == "acknowledge"
        with pytest.raises(ValueError, match="dismiss reason"):
            apply_alert_action(f"sqlite:///{db}", "ACC-M3", "dismiss", "short")
        assert alert_actions(f"sqlite:///{db}", "ACC-M3")[0]["action"] == "acknowledge"
        assert alert_status(f"sqlite:///{db}", "ACC-M3") == "acknowledge"
        compensating = apply_alert_action(f"sqlite:///{db}", "ACC-M3", "escalate")
        rollback_alert_action(f"sqlite:///{db}", "ACC-M3", compensating["action"], compensating["created_at"])
        assert alert_status(f"sqlite:///{db}", "ACC-M3") == "acknowledge"
        timeline = case_evidence(f"sqlite:///{db}", "CASE-001")
        assert timeline and timeline[0]["txn_id"]
        chronology = chronology_summary(f"sqlite:///{db}", "CASE-001")
        assert chronology["pair_accuracy"] >= 0.95 and chronology["evaluated_pairs"] > 0
        evaluation = evaluation_summary(f"sqlite:///{db}")
        assert evaluation["available"] is True
        assert evaluation["transaction_event_coverage"]["covered"] == 2
        account_number = json.loads((demo / "accounts.json").read_text(encoding="utf-8"))[0]["account_number"]
        assert search_entities(f"sqlite:///{db}", account_number[:6])
        with pytest.raises(ValueError):
            search_entities(f"sqlite:///{db}", "123")
        masked = mask_text("Call +91 90000 00101 or transfer 123456789012 to analyst@example.com")
        assert "90000 00101" not in masked and "123456789012" not in masked and "analyst@example.com" not in masked
        event = {"event_id": "LIVE-001", "kind": "victim_payment", "from_account": "ACC-V1", "to_account": "ACC-M3", "amount_inr": 12000, "ts": "2026-01-03T10:00:00Z", "channel": "upi", "reference": "runtime-test"}
        assert ingest_transaction(f"sqlite:///{db}", event)["status"] == "accepted"
        assert ingest_transaction(f"sqlite:///{db}", event)["status"] == "duplicate"
        with pytest.raises(ValueError, match="unknown event fields"):
            ingest_transaction(f"sqlite:///{db}", {**event, "unexpected": True})
        withdrawal = {"event_id": "LIVE-W1", "kind": "cash_withdrawal", "from_account": "ACC-M3", "amount_inr": 5000, "ts": "2026-01-03T11:00:00Z", "channel": "atm", "reference": "runtime-withdrawal"}
        assert ingest_transaction(f"sqlite:///{db}", withdrawal)["status"] == "accepted"
        repeat = load_dataset(demo, f"sqlite:///{db}")
        assert repeat["counts"]["evidence"] == 138
        manifest = json.loads((demo / "manifest.json").read_text(encoding="utf-8")); manifest["synthetic"] = False
        (demo / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(ValueError, match="synthetic"):
            load_dataset(demo, f"sqlite:///{db}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


@pytest.mark.parametrize(("score", "expected"), [(0, "low"), (24, "low"), (25, "medium"), (49, "medium"), (50, "high"), (74, "high"), (75, "critical"), (100, "critical")])
def test_risk_band_boundaries(score, expected):
    assert _risk_band(score) == expected


def test_victim_score_clamps_and_seeded_boundary_is_deterministic():
    assert _victim_score(0, 0, 0, False) == 0
    assert _victim_score(100, 100, 10_000_000_000, True) == 100
    assert _victim_score(1, 1, 0, False) == _victim_score(1, 1, 0, False)


def test_decoy_risk_profile_exposes_mitigation_and_disclaimer():
    db = Path.cwd() / "data" / "runtime" / "fraudmesh.db"
    profile = risk_profile(f"sqlite:///{db}", "ACC-D1")
    assert profile and profile["band"] in {"low", "medium"}
    assert profile["mitigation_points"] <= 0
    assert profile["mitigations"]
    assert profile["disclaimer"] == "Investigation priority, not an indicator of guilt."
