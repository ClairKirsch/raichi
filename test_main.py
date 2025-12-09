from fastapi import testclient
from main import app
client = testclient.TestClient(app)

jwt_token = ""

def test_read_venue_not_found():
    response = client.get("/venues/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Venue not found"}

