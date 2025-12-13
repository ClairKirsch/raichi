from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from main import app
import os.path
import pyotp

jwt_token = ""
twofactor_uri = ""


def test_user_registration():
    if os.path.exists("database.db"):  # Hack until this is moved to Postgres
        os.remove("database.db")

    with TestClient(app) as client:
        response = client.post(
            "/users/", json={"username": "testuser", "password": "testpassword"}
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


def test_update_user_profile():
    with TestClient(app) as client:
        response = client.put(
            "/users/me/",
            json={
                "full_name": "Test User",
                "email": "shinozawa749@gmail.com",
                "bio": "This is a test user.",
                "profile_image": "http://example.com/image.jpg",
            },
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert response.status_code == 200
        response = client.get(
            "/users/me/", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("full_name") == "Test User"
        assert response.json().get("email") == "shinozawa749@gmail.com"
        assert response.json().get("bio") == "This is a test user."
        assert response.json().get("profile_image") == "http://example.com/image.jpg"


def test_create_venue():
    with TestClient(app) as client:
        response = client.post(
            "/venues/",
            json={
                "name": "Test Venue",
                "address": "123 Test St",
                "latitude": 40.7128,
                "longitude": -74.0060,
            },
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        print(response.json())
        assert response.status_code == 200


def test_get_venue():
    with TestClient(app) as client:
        response = client.get(
            "/venues/1", headers={"Authorization": f"Bearer {jwt_token}"}
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
                "date": (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "venue_id": 1,
            },
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert response.status_code == 200


def test_get_event():
    with TestClient(app) as client:
        response = client.get(
            "/events/1", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("title") == "Test Event"
        assert response.json().get("description") == "This is a test event."
        assert response.json().get("date") == (
            datetime.today() + timedelta(days=1)
        ).strftime("%Y-%m-%dT00:00:00")
        assert response.json().get("venue").get("name") == "Test Venue"
        assert response.json().get("venue").get("address") == "123 Test St"
        assert response.json().get("venue").get("latitude") == 40.7128
        assert response.json().get("venue").get("longitude") == -74.0060


def test_attend_event():
    with TestClient(app) as client:
        response = client.post(
            "/events/1/attend", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("detail") == "User is now attending the event"
        response = client.get(
            "/users/me/", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert len(response.json().get("events")) == 1
        assert response.json().get("events")[0].get("title") == "Test Event"
        assert (
            response.json().get("events")[0].get("description")
            == "This is a test event."
        )
        assert response.json().get("events")[0].get("date") == (
            datetime.today() + timedelta(days=1)
        ).strftime("%Y-%m-%dT00:00:00")


def test_unattend_event():
    with TestClient(app) as client:
        response = client.post(
            "/events/1/unattend", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("detail") == "User has unattended the event"
        response = client.get(
            "/users/me/", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert len(response.json().get("events")) == 0


def test_send_message():
    with TestClient(app) as client:
        response = client.post(
            "/users/", json={"username": "testuser2", "password": "testpassword"}
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

        response = client.post(
            "/events/1/attend", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("detail") == "User is now attending the event"

        response = client.post(
            "/events/1/attend", headers={"Authorization": f"Bearer {jwt_token2}"}
        )
        assert response.status_code == 200
        assert response.json().get("detail") == "User is now attending the event"

        url = f"/message/{1}/send"
        params = {
            "subject": "Test Subject",
            "message": "This is a test message.",
        }

        # Make the POST request
        response = client.post(
            url, params=params, headers={"Authorization": f"Bearer {jwt_token2}"}
        )
        assert response.status_code == 200
        response = client.get(
            "/message/inbox/", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json()[0].get("subject") == "Test Subject"
        assert response.json()[0].get("content") == "This is a test message."


def test_send_message_failure():
    with TestClient(app) as client:
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

        response = client.post(
            "/events/1/unattend", headers={"Authorization": f"Bearer {jwt_token}"}
        )

        url = f"/message/{1}/send"
        params = {
            "subject": "Test Subject",
            "message": "This is a test message.",
            "latitude": 1.0,
            "longitude": 1.0,
        }

        response = client.post(
            url, params=params, headers={"Authorization": f"Bearer {jwt_token2}"}
        )
        assert (
            response.json().get("detail")
            == "You can only message users who share an event with you"
        )


def test_create_tag():
    with TestClient(app) as client:
        response = client.post(
            "/tags/",
            json={
                "name": "Test Tag",
            },
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert response.status_code == 200
        assert response.json().get("name") == "Test Tag"


def test_get_tag():
    with TestClient(app) as client:
        response = client.get(
            "/tags/1", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("name") == "Test Tag"


def test_assign_tag_to_event():
    with TestClient(app) as client:
        response = client.post(
            "/tags/1/associate/1",
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert response.status_code == 200
        assert response.json().get("detail") == "Tag associated with event successfully"


def test_search_events_by_tag():
    with TestClient(app) as client:
        response = client.post(
            "/search/by-tag?tag_name=Test Tag",
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert response.status_code == 200, f"Error: {response.content}"
        assert len(response.json()) > 0
        assert response.json()[0].get("title") == "Test Event"


def test_search_events_by_tag_substring():
    with TestClient(app) as client:
        response = client.post(
            "/search/by-tag?tag_name=Tes",
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert response.status_code == 200, f"Error: {response.content}"
        assert len(response.json()) > 0
        assert response.json()[0].get("title") == "Test Event"


def test_search_events_by_location():
    with TestClient(app) as client:
        response = client.post(
            "/search/by-location?latitude=40.7128&longitude=-74.0060&radius_miles=10",
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert response.status_code == 200, f"Error: {response.content}"
        assert len(response.json()) > 0
        assert response.json()[0].get("title") == "Test Event"


# def test_sending_emails():
#    with TestClient(app) as client:
#        response = client.post(
#            "/events/1/attend", headers={"Authorization": f"Bearer {jwt_token}"}
#        )
#        assert response.status_code == 200
#        assert response.json().get("detail") == "User is now attending the event"
#        response = client.get(
#            "/users/me/", headers={"Authorization": f"Bearer {jwt_token}"}
#        )
#        assert response.status_code == 200
#        assert len(response.json().get("events")) == 1
#        assert response.json().get("events")[0].get("title") == "Test Event"
#        assert (
#            response.json().get("events")[0].get("description")
#            == "This is a test event."
#        )
#        assert response.json().get("events")[0].get("date") == (
#            datetime.today() + timedelta(days=1)
#        ).strftime("%Y-%m-%dT00:00:00")
#        response = client.post("/events/email")
#        assert response.json().get("detail") == "Email reminders sent successfully."
#        assert response.json().get("amount") > 0


def test_otp_creation():
    with TestClient(app) as client:
        response = client.post(
            "/otp/new/", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("secret") is not None


def test_otp_verification():
    global twofactor_uri
    with TestClient(app) as client:
        response = client.post(
            "/otp/new/", headers={"Authorization": f"Bearer {jwt_token}"}
        )
        assert response.status_code == 200
        assert response.json().get("secret") is not None
        twofactor_uri = response.json().get("secret")
        otp = pyotp.parse_uri(twofactor_uri)
        response = client.post(
            "/otp/verify/",
            json={"otp": otp.now()},
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert response.status_code == 200
        assert response.json().get("detail") == "OTP verified successfully."


def test_user_login_with_otp():
    with TestClient(app) as client:
        global twofactor_uri
        otp = pyotp.parse_uri(twofactor_uri)
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpassword",
                "otp": str(otp.now()),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        jwt_token = response.json().get("access_token")
        assert jwt_token is not None


def test_user_login_fail_with_otp():
    with TestClient(app) as client:
        global twofactor_uri
        otp = pyotp.parse_uri(twofactor_uri)
        response = client.post(
            "/token",
            data={
                "username": "testuser",
                "password": "testpassword",
                "otp": str(00000000),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401
        assert response.json().get("detail") == "Incorrect username, password, or OTP"
        jwt_token = response.json().get("access_token")
        assert jwt_token is None
