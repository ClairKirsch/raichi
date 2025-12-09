from fastapi.testclient import TestClient
from main import app

jwt_token = ""

def test_read_venue_not_found():
    with TestClient(app) as client:
        response = client.get("/venues/9999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Venue not found"}
