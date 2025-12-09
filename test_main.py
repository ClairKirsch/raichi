from fastapi.testclient import TestClient
from main import app
import os.path

jwt_token = ""

def test_user_registration():
    if os.path.exists("database.db"): # Hack until this is moved to Postgres
        os.remove("database.db")
    
    with TestClient(app) as client:
        response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "password": "testpassword"
            }
        )
        assert response.status_code == 200

def test_user_login():
    global jwt_token
    with TestClient(app) as client:
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpassword",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        jwt_token = response.json().get("access_token")
        assert jwt_token is not None

def test_create_venue():
    with TestClient(app) as client:
        response = client.post(
            "/venues/",
            json={
                "name": "Test Venue",
                "address": "123 Test St",
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        print(response.json())
        assert response.status_code == 200
