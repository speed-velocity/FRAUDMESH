from app.main import create_app


def test_health_contract():
    app = create_app()
    assert app.title == "FraudMesh API"
    health_route = next(route for route in app.routes if getattr(route, "path", None) == "/api/v1/health")
    assert health_route.methods == {"GET"}

