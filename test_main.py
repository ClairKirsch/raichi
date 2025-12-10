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

def test_get_venue():
    with TestClient(app) as client:
        response = client.get(
            "/venues/1",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("name") == "Test Venue"
        assert response.json().get("address") == "123 Test St"
        assert response.json().get("latitude") == 40.7128
        assert response.json().get("longitude") == -74.0060

def test_create_event():
    with TestClient(app) as client:
        response = client.post(
            "/events/",
            json={
                "title": "Test Event",
                "description": "This is a test event.",
                "date": "2025-12-31",
                "venue_id": 1
            },
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200

def test_get_event():
    with TestClient(app) as client:
        response = client.get(
            "/events/1",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("title") == "Test Event"
        assert response.json().get("description") == "This is a test event."
        assert response.json().get("date") == "2025-12-31"
        assert response.json().get("venue").get("name") == "Test Venue"
        assert response.json().get("venue").get("address") == "123 Test St"
        assert response.json().get("venue").get("latitude") == 40.7128
        assert response.json().get("venue").get("longitude") == -74.0060

def test_attend_event():
    with TestClient(app) as client:
        response = client.post(
            "/events/1/attend",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("message") == "User is now attending the event"
        response = client.get(
            "/users/me/",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert len(response.json().get("events")) == 1
        assert response.json().get("events")[0].get("title") == "Test Event"
        assert response.json().get("events")[0].get("description") == "This is a test event."
        assert response.json().get("events")[0].get("date") == "2025-12-31"



def test_unattend_event():
    with TestClient(app) as client:
        response = client.post(
            "/events/1/unattend",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("message") == "User has unattended the event"
        response = client.get(
            "/users/me/",
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert len(response.json().get("events")) == 0

def test_send_message():
    with TestClient(app) as client:
        response = client.post(
            "/users/",
            json={
                "username": "testuser2",
                "password": "testpassword"
            }
        )
        assert response.status_code == 200
        response = client.post(
            "/token",
            data={
                "username": "testuser2",
                "password": "testpassword",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        jwt_token2 = response.json().get("access_token")
        assert jwt_token2 is not None
        url = f"/message/{1}/send"
        params = {
            "subject": "Test Subject",
            "message": "This is a test message.",
            "latitude": 1.0,
            "longitude": 1.0,
        }

        # Make the POST request
        response = client.post(
            url,
            params=params,
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        response = client.get("/message/inbox/", headers={"Authorization": f"Bearer {jwt_token}"})
        assert response.status_code == 200
        assert response.json()[0].get("subject") == "Test Subject"
        assert response.json()[0].get("content") == "This is a test message."
