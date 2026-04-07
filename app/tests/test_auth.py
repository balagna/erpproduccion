def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Iniciar sesi" in response.data

def test_health_api(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["ok"] is True

def test_stats_api_unauthorized(client):
    response = client.get("/api/stats")
    assert response.status_code == 401

def test_stats_api_authorized(client):
    response = client.get("/api/stats", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data
    assert data["users"] >= 1
