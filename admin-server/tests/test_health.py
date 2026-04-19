from app import create_app


def test_health_check():
    app = create_app("testing")

    with app.test_client() as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["data"]["service"] == "admin-server"

