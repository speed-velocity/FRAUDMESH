from contextlib import asynccontextmanager
from collections import defaultdict, deque
from pathlib import Path
from time import monotonic
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, Body, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.reasoning.client import NemotronClient
from app.reasoning.live import run_live_reasoning
from app.reasoning.nemo import MAX_HISTORY, answer_nemo, validate_page_context
from app.db.database import alert_actions, alert_status, append_audit, apply_alert_action, audit_records, authenticate_user, case_contradictions, case_evidence, case_subgraph, cases_for_entity, chronology_summary, complaint_extraction, contradiction_catalog, create_case, create_finding, create_hypothesis, create_link, create_plan_step, current_summary, edge_detail, ensure_demo_users, entity_detail, evidence_detail, evidence_records, evaluation_summary, ingest_transaction, ingested_events, list_cases, list_findings, list_hypotheses, list_links, list_plan_steps, list_users, narrative_links, network_path, network_summary, review_finding, review_link, review_plan_item, risk_alerts, risk_profile, rollback_alert_action, run_grounded_reasoning, search_entities, session_user, revoke_session, simulator_reset, simulator_status, simulator_step, update_case_notes, update_case_status


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    ensure_demo_users(settings.database_url, settings.demo_investigator_password, settings.demo_admin_password)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="FraudMesh API",
        version="0.1.0",
        docs_url=None if settings.app_env == "prod" else "/docs",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    rate_windows: dict[tuple[str, str], deque[float]] = defaultdict(deque)
    rate_lock = Lock()

    def rate_limited(bucket: str, key: str, limit: int) -> bool:
        now = monotonic()
        cutoff = now - 60
        with rate_lock:
            window = rate_windows[(bucket, key)]
            while window and window[0] <= cutoff:
                window.popleft()
            if len(window) >= max(1, limit):
                return True
            window.append(now)
            return False

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        response = JSONResponse({"detail": "Request validation failed", "code": "validation_error", "request_id": request_id, "errors": exc.errors()}, status_code=422)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        client_key = request.client.host if request.client else "unknown"
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > settings.max_request_body_bytes:
            response = JSONResponse({"detail": "Request body too large", "code": "request_too_large", "request_id": request_id}, status_code=413)
            response.headers["X-Request-ID"] = request_id
            return response
        if request.url.path == "/api/v1/auth/login" and rate_limited("login", client_key, settings.login_rate_limit_per_minute):
            response = JSONResponse({"detail": "Too many login attempts", "code": "rate_limited", "request_id": request_id}, status_code=429)
            response.headers["Retry-After"] = "60"
            response.headers["X-Request-ID"] = request_id
            return response
        expensive_prefixes = ("/api/v1/reasoning", "/api/v1/events", "/api/v1/simulator", "/api/v1/network/path", "/api/chat")
        if request.url.path.startswith(expensive_prefixes) and rate_limited("expensive", client_key, settings.expensive_rate_limit_per_minute):
            response = JSONResponse({"detail": "Request rate limit exceeded", "code": "rate_limited", "request_id": request_id}, status_code=429)
            response.headers["Retry-After"] = "60"
            response.headers["X-Request-ID"] = request_id
            return response
        public_paths = {"/api/v1/health", "/api/v1/auth/login"}
        if settings.app_env in {"demo", "prod"} and request.url.path.startswith("/api/v1/") and request.url.path not in public_paths and request.method != "OPTIONS":
            authorization = request.headers.get("Authorization", "")
            token = authorization.removeprefix("Bearer ").strip() if authorization.startswith("Bearer ") else ""
            if not token or not session_user(settings.database_url, token, settings.jwt_secret, settings.token_key_id, settings.token_issuer, settings.token_audience):
                response = JSONResponse({"detail": "Not authenticated", "request_id": request_id}, status_code=401)
                response.headers["X-Request-ID"] = request_id
                return response
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' http://127.0.0.1:8000 http://localhost:8000 https://fraudmesh-api.onrender.com; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.get("/api/v1/health")
    async def health() -> JSONResponse:
        summary = current_summary(settings.database_url)
        configured = NemotronClient(settings.nemotron_base_url, settings.nemotron_api_key, settings.nemotron_model).configured
        return JSONResponse({"status": "ok", "service": "fraudmesh", "reasoning": {"live_configured": configured}, **summary})

    @app.get("/")
    async def root() -> JSONResponse:
        return JSONResponse({
            "service": "fraudmesh-api",
            "status": "online",
            "health": "/api/v1/health",
            "frontend": "https://fraudmesh-ui.onrender.com",
        })

    @app.get("/api/v1/meta/limitations")
    async def limitations() -> JSONResponse:
        return JSONResponse({
            "prototype_mode": True,
            "controls": [
                {"name": "Synthetic data boundary", "status": "active", "detail": "Only explicitly synthetic datasets are accepted."},
                {"name": "Human review", "status": "required", "detail": "Alerts and cases never trigger automatic enforcement action."},
                {"name": "Explainable scoring", "status": "active", "detail": "Current risk signals expose deterministic reasons and amounts."},
                {"name": "Nemotron reasoning", "status": "active", "detail": "Live smoke and validated CASE-001 reasoning recording are available; browser review remains human-controlled."},
                {"name": "Authentication and audit hardening", "status": "partial", "detail": "Nimbus-style signed access tokens, server-side revocation, session expiry, lockout, role checks, and audit storage are implemented."},
            ],
        })

    @app.get("/api/v1/reasoning/status")
    async def reasoning_status() -> JSONResponse:
        settings_now = get_settings()
        cached_dir = Path("data/demo/cached_reasoning")
        if not cached_dir.exists():
            cached_dir = Path(__file__).resolve().parents[2] / "data" / "demo" / "cached_reasoning"
        client_now = NemotronClient(settings_now.nemotron_base_url, settings_now.nemotron_api_key, settings_now.nemotron_model)
        missing = client_now.missing_configuration
        return JSONResponse({"live_configured": not missing, "missing": missing, "cached_available": cached_dir.exists() and any(cached_dir.glob("*.json")), "cached_label": "Sample recording · Cached (not live)", "live_label": "Live Nemotron · Nebius Token Factory", "human_review_required": True})

    def bearer_user(request: Request) -> dict | None:
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        return session_user(settings.database_url, header.removeprefix("Bearer ").strip(), settings.jwt_secret, settings.token_key_id, settings.token_issuer, settings.token_audience)

    @app.post("/api/v1/auth/login")
    async def login(payload: dict = Body(...), request: Request = None) -> JSONResponse:
        username = str(payload.get("username", "")); password = str(payload.get("password", ""))
        result = authenticate_user(settings.database_url, username, password, settings.session_minutes, settings.jwt_secret, settings.token_key_id, settings.token_issuer, settings.token_audience)
        request_id = request.headers.get("X-Request-ID") if request else None
        if not result:
            append_audit(settings.database_url, None, None, "login", "denied", request_id, details={"username": username[:80]})
            return JSONResponse({"detail": "Invalid username or password"}, status_code=401)
        append_audit(settings.database_url, result["user_id"], result["role"], "login", "success", request_id)
        return JSONResponse({"access_token": result["access_token"], "token_type": "bearer", "expires_at": result["expires_at"], "user": {"user_id": result["user_id"], "username": result["username"], "role": result["role"]}})

    @app.get("/api/v1/auth/me")
    async def me(request: Request) -> JSONResponse:
        user = bearer_user(request)
        if not user: return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        return JSONResponse(user)

    @app.post("/api/v1/auth/logout")
    async def logout(request: Request) -> JSONResponse:
        header = request.headers.get("Authorization", "")
        user = bearer_user(request)
        if not user: return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        revoke_session(settings.database_url, header.removeprefix("Bearer ").strip(), settings.jwt_secret, settings.token_key_id, settings.token_issuer, settings.token_audience)
        append_audit(settings.database_url, user["user_id"], user["role"], "logout", "success", request.headers.get("X-Request-ID"))
        return JSONResponse({"status": "logged_out"})

    @app.get("/api/v1/audit")
    async def audit(request: Request, limit: int = 100, offset: int = 0) -> JSONResponse:
        user = bearer_user(request)
        if not user: return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        if user["role"] != "admin": return JSONResponse({"detail": "You do not have access to this action."}, status_code=403)
        append_audit(settings.database_url, user["user_id"], user["role"], "audit_view", "success", request.headers.get("X-Request-ID"))
        bounded_limit = min(max(limit, 1), 200); bounded_offset = max(offset, 0)
        records = audit_records(settings.database_url, bounded_limit, bounded_offset)
        return JSONResponse({"records": records, "limit": bounded_limit, "offset": bounded_offset, "next_offset": bounded_offset + bounded_limit if len(records) == bounded_limit else None})

    @app.get("/api/v1/users")
    async def users(request: Request) -> JSONResponse:
        user = bearer_user(request)
        if not user: return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        if user["role"] != "admin": return JSONResponse({"detail": "You do not have access to this action."}, status_code=403)
        return JSONResponse({"users": list_users(settings.database_url)})

    @app.get("/api/v1/datasets/current")
    async def current_dataset() -> JSONResponse:
        return JSONResponse(current_summary(settings.database_url))

    @app.get("/api/v1/dashboard/summary")
    async def dashboard_summary() -> JSONResponse:
        summary = current_summary(settings.database_url)
        alerts = risk_alerts(settings.database_url)
        for item in alerts:
            item["status"] = alert_status(settings.database_url, item["entity_id"])
        return JSONResponse({"dataset_loaded": summary["dataset_loaded"], "counts": summary["counts"], "top_priority": alerts[:3], "alerts": alerts, "state_version": "risk-v1"})

    @app.get("/api/v1/risk/{entity_id}")
    async def risk(entity_id: str) -> JSONResponse:
        profile = risk_profile(settings.database_url, entity_id)
        if not profile:
            return JSONResponse({"detail": "entity not found", "code": "entity_not_found"}, status_code=404)
        return JSONResponse(profile)

    @app.get("/api/v1/alerts")
    async def alerts(severity: str | None = None, status: str | None = None, rule: str | None = None, date_from: str | None = None, date_to: str | None = None) -> JSONResponse:
        records = risk_alerts(settings.database_url)
        allowed_severities = {"info", "warning", "medium", "high", "critical"}
        if severity and severity.lower() not in allowed_severities:
            return JSONResponse({"detail": "Unsupported severity filter"}, status_code=422)
        if severity: records = [item for item in records if item["severity"].lower() == severity.lower()]
        if rule: records = [item for item in records if rule.upper() in item.get("rules_fired", [])]
        if date_from: records = [item for item in records if (item.get("created_at") or "") >= date_from]
        if date_to: records = [item for item in records if (item.get("created_at") or "") <= date_to]
        for item in records: item["status"] = alert_status(settings.database_url, item["entity_id"])
        if status: records = [item for item in records if item["status"] == status.lower()]
        return JSONResponse({"alerts": records, "state_version": "risk-v1", "filters": {"severity": severity, "status": status, "rule": rule, "date_from": date_from, "date_to": date_to}})

    @app.post("/api/v1/alerts/{entity_id}/action")
    async def alert_action(entity_id: str, payload: dict = Body(...), request: Request = None) -> JSONResponse:
        try:
            action = str(payload.get("action", "")); result = apply_alert_action(settings.database_url, entity_id, action, str(payload.get("reason", "")))
            if action == "escalate":
                existing = cases_for_entity(settings.database_url, entity_id)
                if existing:
                    result["case"] = existing[0]; result["case_action"] = "attached"
                else:
                    alert = next((item for item in risk_alerts(settings.database_url) if item["entity_id"] == entity_id), None)
                    created = create_case(settings.database_url, entity_id, int(alert["score"] if alert else 0), f"Escalated review · {entity_id}", "Created from an investigator escalation.")
                    result["case"] = created; result["case_action"] = "created"
            actor = bearer_user(request) if request else None
            try:
                append_audit(settings.database_url, actor["user_id"] if actor else None, actor["role"] if actor else None, f"alert_{result['action']}", "success", request.headers.get("X-Request-ID") if request else None, "alert", entity_id)
            except Exception:
                rollback_alert_action(settings.database_url, entity_id, result["action"], result["created_at"])
                raise
            return JSONResponse(result)
        except ValueError as exc: return JSONResponse({"detail": str(exc), "code": "invalid_alert_action"}, status_code=400)

    @app.get("/api/v1/alerts/{entity_id}/actions")
    async def alert_action_history(entity_id: str) -> JSONResponse:
        return JSONResponse({"actions": alert_actions(settings.database_url, entity_id)})

    @app.post("/api/v1/events")
    async def ingest_event(request: Request, payload: dict = Body(...)) -> JSONResponse:
        user = bearer_user(request)
        if not user:
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        try:
            result = ingest_transaction(settings.database_url, payload)
            append_audit(settings.database_url, user["user_id"], user["role"], "event_ingest", result["status"], request.headers.get("X-Request-ID"), "event", str(payload.get("event_id", "")))
            return JSONResponse(result, status_code=202 if result["status"] == "accepted" else 200)
        except ValueError as exc:
            return JSONResponse({"detail": str(exc), "code": "invalid_event"}, status_code=400)

    @app.get("/api/v1/events")
    async def events(limit: int = 25, offset: int = 0) -> JSONResponse:
        bounded_limit = min(max(limit, 1), 100); bounded_offset = max(offset, 0)
        records = ingested_events(settings.database_url, bounded_limit, bounded_offset)
        return JSONResponse({"events": records, "limit": bounded_limit, "offset": bounded_offset, "next_offset": bounded_offset + bounded_limit if len(records) == bounded_limit else None})

    @app.get("/api/v1/simulator/status")
    async def simulator() -> JSONResponse:
        return JSONResponse(simulator_status(settings.database_url))

    @app.post("/api/v1/simulator/reset")
    async def reset_simulator() -> JSONResponse:
        return JSONResponse(simulator_reset(settings.database_url))

    @app.post("/api/v1/simulator/step")
    async def step_simulator() -> JSONResponse:
        return JSONResponse(simulator_step(settings.database_url))

    @app.get("/api/v1/network")
    async def network() -> JSONResponse:
        return JSONResponse(network_summary(settings.database_url))

    @app.get("/api/v1/network/path")
    async def path(source: str = "", target: str = "", max_hops: int = 8) -> JSONResponse:
        try:
            return JSONResponse(network_path(settings.database_url, source, target, max_hops))
        except ValueError as exc:
            return JSONResponse({"detail": str(exc), "code": "invalid_path_query"}, status_code=400)

    @app.get("/api/v1/network/edge")
    async def edge(source: str = "", target: str = "") -> JSONResponse:
        if not source or not target:
            return JSONResponse({"detail": "source and target are required", "code": "invalid_edge_query"}, status_code=400)
        return JSONResponse(edge_detail(settings.database_url, source, target))

    @app.get("/api/v1/links")
    async def links(state: str = "") -> JSONResponse:
        return JSONResponse({"links": list_links(settings.database_url, state)})

    @app.post("/api/v1/links", status_code=201)
    async def add_link(payload: dict = Body(...)) -> JSONResponse:
        try: return JSONResponse(create_link(settings.database_url, str(payload.get("source_entity", "")), str(payload.get("target_entity", "")), str(payload.get("link_type", "inferred")), str(payload.get("strength", "inferred")), list(payload.get("evidence_ids", []))), status_code=201)
        except (ValueError, TypeError) as exc: return JSONResponse({"detail": str(exc), "code": "invalid_link"}, status_code=400)

    @app.post("/api/v1/links/{link_id}/{action}")
    async def link_action(link_id: str, action: str, payload: dict = Body(...), request: Request = None) -> JSONResponse:
        try:
            actor = bearer_user(request) if request else None
            result = review_link(settings.database_url, link_id, action, str(payload.get("reason", "")), actor["user_id"] if actor else None)
            append_audit(settings.database_url, actor["user_id"] if actor else None, actor["role"] if actor else None, f"link_{action}", "success", request.headers.get("X-Request-ID") if request else None, "link", link_id)
            return JSONResponse(result)
        except ValueError as exc: return JSONResponse({"detail": str(exc), "code": "invalid_link_review"}, status_code=400)

    @app.get("/api/v1/entities/{entity_id}")
    async def entity(entity_id: str) -> JSONResponse:
        result = entity_detail(settings.database_url, entity_id)
        if not result:
            return JSONResponse({"detail": "Entity not found"}, status_code=404)
        return JSONResponse(result)

    @app.get("/api/v1/evidence")
    async def evidence(query: str = "", limit: int = 50, offset: int = 0) -> JSONResponse:
        bounded_limit = min(max(limit, 1), 100); bounded_offset = max(offset, 0)
        records = evidence_records(settings.database_url, query=query, limit=bounded_limit, offset=bounded_offset)
        return JSONResponse({"records": records, "limit": bounded_limit, "offset": bounded_offset, "next_offset": bounded_offset + bounded_limit if len(records) == bounded_limit else None})

    @app.post("/api/v1/evidence/{evidence_id}/unmask")
    async def unmask_evidence(evidence_id: str, request: Request, payload: dict = Body(...)) -> JSONResponse:
        user = bearer_user(request)
        if not user:
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        reason = str(payload.get("reason", "")).strip()
        if len(reason) < 8:
            return JSONResponse({"detail": "A reason of at least 8 characters is required", "code": "reason_required"}, status_code=400)
        record = evidence_detail(settings.database_url, evidence_id)
        if not record:
            return JSONResponse({"detail": "Evidence not found"}, status_code=404)
        append_audit(settings.database_url, user["user_id"], user["role"], "evidence_unmask", "success", request.headers.get("X-Request-ID"), "evidence", evidence_id, {"reason": reason[:200]})
        return JSONResponse(record)

    @app.get("/api/v1/search")
    async def search(q: str = "", limit: int = 25) -> JSONResponse:
        try:
            return JSONResponse({"query": q, "results": search_entities(settings.database_url, query=q, limit=limit)})
        except ValueError as exc:
            return JSONResponse({"detail": str(exc), "code": "invalid_search_query"}, status_code=400)

    @app.get("/api/v1/narrative-links")
    async def narrative_link_review() -> JSONResponse:
        return JSONResponse({"links": narrative_links(settings.database_url), "matching": "exact", "human_confirmation_required": True})

    @app.get("/api/v1/complaints/extraction")
    async def complaints_extraction() -> JSONResponse:
        return JSONResponse(complaint_extraction(settings.database_url))

    @app.get("/api/v1/contradictions")
    async def contradiction_review() -> JSONResponse:
        return JSONResponse({"conflicts": contradiction_catalog(settings.database_url), "software_values_authoritative": True, "count": len(contradiction_catalog(settings.database_url))})

    @app.get("/api/v1/cases")
    async def cases() -> JSONResponse:
        return JSONResponse({"cases": list_cases(settings.database_url)})

    @app.get("/api/v1/cases/offer")
    async def case_offer(entity_id: str = "") -> JSONResponse:
        if not entity_id.strip():
            return JSONResponse({"existing": []})
        return JSONResponse({"existing": cases_for_entity(settings.database_url, entity_id.strip())})

    @app.post("/api/v1/cases", status_code=201)
    async def create_investigation_case(payload: dict = Body(...), request: Request = None) -> JSONResponse:
        try:
            result = create_case(settings.database_url, str(payload.get("entity_id", "")), int(payload.get("score", 0)), str(payload.get("title", "Investigation review")), str(payload.get("notes", "")))
            actor = bearer_user(request) if request else None
            append_audit(settings.database_url, actor["user_id"] if actor else None, actor["role"] if actor else None, "case_create", "success", request.headers.get("X-Request-ID") if request else None, "case", result["case_id"], {"entity_id": result["entity_id"]})
            return JSONResponse(result, status_code=201)
        except (ValueError, TypeError) as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.put("/api/v1/cases/{case_id}/notes")
    async def save_case_notes(case_id: str, payload: dict = Body(...), request: Request = None) -> JSONResponse:
        result = update_case_notes(settings.database_url, case_id, str(payload.get("notes", "")))
        if not result:
            return JSONResponse({"detail": "Case not found"}, status_code=404)
        actor = bearer_user(request) if request else None
        append_audit(settings.database_url, actor["user_id"] if actor else None, actor["role"] if actor else None, "case_notes_update", "success", request.headers.get("X-Request-ID") if request else None, "case", case_id)
        return JSONResponse(result)

    @app.get("/api/v1/cases/{case_id}/evidence")
    async def investigation_case_evidence(case_id: str) -> JSONResponse:
        return JSONResponse({"records": case_evidence(settings.database_url, case_id)})

    @app.get("/api/v1/cases/{case_id}/subgraph")
    async def investigation_case_subgraph(case_id: str) -> JSONResponse:
        return JSONResponse(case_subgraph(settings.database_url, case_id))

    @app.get("/api/v1/cases/{case_id}/contradictions")
    async def investigation_case_contradictions(case_id: str) -> JSONResponse:
        return JSONResponse({"conflicts": case_contradictions(settings.database_url, case_id), "software_values_authoritative": True})

    @app.get("/api/v1/cases/{case_id}/chronology")
    async def investigation_case_chronology(case_id: str) -> JSONResponse:
        return JSONResponse(chronology_summary(settings.database_url, case_id))

    @app.get("/api/v1/cases/{case_id}/findings")
    async def findings(case_id: str) -> JSONResponse:
        return JSONResponse({"findings": list_findings(settings.database_url, case_id)})

    @app.post("/api/v1/cases/{case_id}/findings", status_code=201)
    async def add_finding(case_id: str, payload: dict = Body(...), request: Request = None) -> JSONResponse:
        try:
            result = create_finding(settings.database_url, case_id, str(payload.get("statement", "")), list(payload.get("evidence_ids", [])), str(payload.get("source", "Deterministic")), float(payload.get("confidence", 0.5)))
            actor = bearer_user(request) if request else None
            append_audit(settings.database_url, actor["user_id"] if actor else None, actor["role"] if actor else None, "finding_create", "success", request.headers.get("X-Request-ID") if request else None, "finding", result["finding_id"])
            return JSONResponse(result, status_code=201)
        except (ValueError, TypeError) as exc:
            return JSONResponse({"detail": str(exc), "code": "invalid_finding"}, status_code=400)

    @app.post("/api/v1/findings/{finding_id}/review")
    async def review(finding_id: str, payload: dict = Body(...), request: Request = None) -> JSONResponse:
        try:
            actor = bearer_user(request) if request else None
            result = review_finding(settings.database_url, finding_id, str(payload.get("state", "")), str(payload.get("reason", "")), actor["user_id"] if actor else None)
            append_audit(settings.database_url, actor["user_id"] if actor else None, actor["role"] if actor else None, "finding_review", "success", request.headers.get("X-Request-ID") if request else None, "finding", finding_id, {"state": result["review_state"]})
            return JSONResponse(result)
        except ValueError as exc:
            return JSONResponse({"detail": str(exc), "code": "invalid_review"}, status_code=400)

    @app.get("/api/v1/cases/{case_id}/hypotheses")
    async def hypotheses(case_id: str) -> JSONResponse:
        return JSONResponse({"hypotheses": list_hypotheses(settings.database_url, case_id)})

    @app.post("/api/v1/cases/{case_id}/hypotheses", status_code=201)
    async def add_hypothesis(case_id: str, payload: dict = Body(...)) -> JSONResponse:
        try: return JSONResponse(create_hypothesis(settings.database_url, case_id, str(payload.get("statement", "")), list(payload.get("evidence_ids", [])), float(payload.get("confidence", 0.5))), status_code=201)
        except (ValueError, TypeError) as exc: return JSONResponse({"detail": str(exc), "code": "invalid_hypothesis"}, status_code=400)

    @app.get("/api/v1/cases/{case_id}/plan")
    async def plan(case_id: str) -> JSONResponse:
        return JSONResponse({"steps": list_plan_steps(settings.database_url, case_id)})

    @app.post("/api/v1/cases/{case_id}/reasoning")
    async def run_reasoning(case_id: str, payload: dict = Body(default={}), request: Request = None) -> JSONResponse:
        try:
            mode = str(payload.get("mode", "cached"))
            if mode == "live":
                client = NemotronClient(settings.nemotron_base_url, settings.nemotron_api_key, settings.nemotron_model, settings.nemotron_timeout_s, max_tokens=settings.nemotron_max_tokens)
                if not client.configured:
                    return JSONResponse({"detail": f"Live Nemotron reasoning unavailable. Missing or invalid: {', '.join(client.missing_configuration)}", "missing": client.missing_configuration, "code": "reasoning_unavailable"}, status_code=503)
                result = await run_live_reasoning(settings.database_url, case_id, client)
            else:
                result = run_grounded_reasoning(settings.database_url, case_id, mode)
            actor = bearer_user(request) if request else None
            if actor:
                append_audit(settings.database_url, actor["user_id"], actor["role"], "reasoning_run", "success", request.headers.get("X-Request-ID"), "case", case_id, {"mode": result["mode"]})
            return JSONResponse(result)
        except ValueError as exc:
            return JSONResponse({"detail": str(exc), "code": "reasoning_unavailable"}, status_code=400)

    @app.post("/api/v1/alerts/{entity_id}/reasoning")
    async def explain_alert(entity_id: str, request: Request = None) -> JSONResponse:
        """Run live reasoning for an alert using server-side case/evidence context."""
        linked_cases = cases_for_entity(settings.database_url, entity_id)
        if not linked_cases:
            return JSONResponse({"detail": "Open an investigation case for this alert before requesting reasoning.", "code": "case_required"}, status_code=400)
        try:
            client = NemotronClient(settings.nemotron_base_url, settings.nemotron_api_key, settings.nemotron_model, settings.nemotron_timeout_s, max_tokens=settings.nemotron_max_tokens)
            if not client.configured:
                return JSONResponse({"detail": f"Live Nemotron reasoning unavailable. Missing or invalid: {', '.join(client.missing_configuration)}", "missing": client.missing_configuration, "code": "reasoning_unavailable"}, status_code=503)
            result = await run_live_reasoning(settings.database_url, linked_cases[0]["case_id"], client)
            actor = bearer_user(request) if request else None
            if actor:
                append_audit(settings.database_url, actor["user_id"], actor["role"], "alert_reasoning", "success", request.headers.get("X-Request-ID"), "entity", entity_id, {"case_id": linked_cases[0]["case_id"], "provider": "Nebius Token Factory"})
            return JSONResponse(result)
        except ValueError as exc:
            return JSONResponse({"detail": str(exc), "code": "reasoning_unavailable"}, status_code=400)

    nemo_history: dict[tuple[str, str], deque[dict]] = defaultdict(lambda: deque(maxlen=MAX_HISTORY))

    @app.post("/api/chat")
    async def nemo_chat(payload: dict = Body(...), request: Request = None) -> JSONResponse:
        actor = bearer_user(request) if request else None
        if not actor:
            return JSONResponse({"detail": "Not authenticated", "code": "not_authenticated"}, status_code=401)
        message = payload.get("message") if isinstance(payload, dict) else None
        if not isinstance(message, str) or not message.strip():
            return JSONResponse({"detail": "Message is required", "code": "invalid_message"}, status_code=422)
        if len(message) > 1200:
            return JSONResponse({"detail": "Message is too long. Keep it under 1,200 characters.", "code": "message_too_long"}, status_code=422)
        try:
            page_context = validate_page_context(payload.get("page_context"))
            conversation_id = str(payload.get("conversation_id") or "default")[:80]
            if not conversation_id or not all(character.isalnum() or character in "_-" for character in conversation_id):
                return JSONResponse({"detail": "conversation_id is invalid", "code": "invalid_conversation"}, status_code=422)
        except ValueError as exc:
            return JSONResponse({"detail": str(exc), "code": "invalid_page_context"}, status_code=422)
        if rate_limited("nemo", actor["user_id"], settings.expensive_rate_limit_per_minute):
            return JSONResponse({"detail": "Nemo request rate limit exceeded", "code": "rate_limited"}, status_code=429, headers={"Retry-After": "60"})
        client = NemotronClient(settings.nemotron_base_url, settings.nemotron_api_key, settings.nemotron_model, settings.nemotron_timeout_s, max_tokens=settings.nemotron_max_tokens)
        audit_details = {key: value for key, value in page_context.items()}
        try:
            if not client.configured:
                append_audit(settings.database_url, actor["user_id"], actor["role"], "nemo_chat", "unavailable", request.headers.get("X-Request-ID"), details=audit_details)
                return JSONResponse({"detail": "Nemo is unavailable", "missing": client.missing_configuration, "code": "nemo_unavailable"}, status_code=503)
            history_key = (actor["user_id"], conversation_id)
            answer = await answer_nemo(settings.database_url, client, message, page_context, list(nemo_history[history_key]))
            nemo_history[history_key].append({"role": "user", "content": message[:1200]})
            nemo_history[history_key].append({"role": "assistant", "content": answer["answer"][:2000]})
            append_audit(settings.database_url, actor["user_id"], actor["role"], "nemo_chat", "success", request.headers.get("X-Request-ID"), details=audit_details)
            return JSONResponse(answer)
        except ValueError as exc:
            append_audit(settings.database_url, actor["user_id"], actor["role"], "nemo_chat", "failure", request.headers.get("X-Request-ID"), details=audit_details)
            return JSONResponse({"detail": str(exc), "code": "nemo_unavailable"}, status_code=503)

    @app.post("/api/v1/cases/{case_id}/plan", status_code=201)
    async def add_plan_step(case_id: str, payload: dict = Body(...)) -> JSONResponse:
        try: return JSONResponse(create_plan_step(settings.database_url, case_id, int(payload.get("rank", 1)), str(payload.get("action", "")), str(payload.get("rationale", "")), list(payload.get("evidence_ids", [])), payload.get("linked_hypothesis")), status_code=201)
        except (ValueError, TypeError) as exc: return JSONResponse({"detail": str(exc), "code": "invalid_plan_step"}, status_code=400)

    @app.post("/api/v1/review/{item_type}/{item_id}")
    async def review_item(item_type: str, item_id: str, payload: dict = Body(...), request: Request = None) -> JSONResponse:
        try:
            actor = bearer_user(request) if request else None
            result = review_plan_item(settings.database_url, item_type, item_id, str(payload.get("state", "")), str(payload.get("reason", "")), actor["user_id"] if actor else None)
            append_audit(settings.database_url, actor["user_id"] if actor else None, actor["role"] if actor else None, "review_item", "success", request.headers.get("X-Request-ID") if request else None, item_type, item_id, {"state": result["review_state"]})
            return JSONResponse(result)
        except ValueError as exc: return JSONResponse({"detail": str(exc), "code": "invalid_review"}, status_code=400)

    @app.put("/api/v1/cases/{case_id}/status")
    async def save_case_status(case_id: str, payload: dict = Body(...), request: Request = None) -> JSONResponse:
        try:
            result = update_case_status(settings.database_url, case_id, str(payload.get("status", "")))
        except ValueError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)
        if not result:
            return JSONResponse({"detail": "Case not found"}, status_code=404)
        actor = bearer_user(request) if request else None
        append_audit(settings.database_url, actor["user_id"] if actor else None, actor["role"] if actor else None, "case_status_update", "success", request.headers.get("X-Request-ID") if request else None, "case", case_id, {"status": result["status"]})
        return JSONResponse(result)

    @app.get("/api/v1/evaluation")
    async def evaluation() -> JSONResponse:
        return JSONResponse(evaluation_summary(settings.database_url))

    return app


app = create_app()
