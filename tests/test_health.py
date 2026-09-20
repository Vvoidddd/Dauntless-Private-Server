def test_root_health_and_readiness(client):
    assert client.get("/").json()["status"] == "running"
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}


def test_readiness_failure_is_structured(client, app, monkeypatch):
    monkeypatch.setattr(app.state.db, "ready", lambda: False)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"error": {"code": "not_ready", "message": "Database is unavailable"}}


def test_unknown_route_has_uniform_error(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "request_error"


def test_openapi_exposes_core_operations(client):
    paths = client.get("/openapi.json").json()["paths"]
    required = {
        "/health", "/ready", "/auth/register", "/auth/login",
        "/auth/validate-token", "/auth/logout", "/auth/profile/me",
    }
    assert required <= set(paths)
    assert paths["/auth/register"]["post"]["responses"]["201"]
