import pytest
from unittest.mock import MagicMock
from APIClient import APIClient

def test_build_url(api_client):

    assert api_client.build_url("/users") == "http://fake-api.local/users"

@pytest.fixture(scope="module")
def api_client():
    client = APIClient(
        base_url="http://fake-api.local"
    )

    def mock_post(path, json):
        fake_response = MagicMock()

        if path == "/login":
            username = (json or {}).get("username", "")
            password = (json or {}).get("password", "")
            if username and password and len(username) >= 3 and len(password) >= 6:
                fake_response.status_code = 200
                fake_response.json.return_value = {"token": "fake_token_123"}
            else:
                fake_response.status_code = 400
                fake_response.json.return_value = {"error": "invalid credentials"}
        elif path == "/register":
            email = (json or {}).get("email", "")
            password = (json or {}).get("password", "")
            if email and "@" in email and password and len(password) >= 6:
                fake_response.status_code = 200
                fake_response.json.return_value = {"user_id": 1001}
            else:
                fake_response.status_code = 400
                fake_response.json.return_value = {"error": "invalid register data"}
        elif path == "/users":
            fake_response.status_code = 200
            fake_response.json.return_value = {"id": 1001, "name": "Test User"}
        else:
            fake_response.status_code = 404
            fake_response.json.return_value = {}
        return fake_response

    client.post = MagicMock(
        side_effect=mock_post
    )
    return client
