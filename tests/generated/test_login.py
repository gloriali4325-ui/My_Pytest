import pytest

test_cases = [
    {
        "name": "valid_login",
        "data": {
            "username": "user1",
            "password": "pass1"
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    },
    {
        "name": "missing_username",
        "data": {
            "username": "",
            "password": "pass1"
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    },
    {
        "name": "missing_password",
        "data": {
            "username": "user1",
            "password": ""
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    },
    {
        "name": "invalid_username",
        "data": {
            "username": "   ",
            "password": "pass1"
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    },
    {
        "name": "short_password",
        "data": {
            "username": "user1",
            "password": "p"
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    }
]

@pytest.mark.parametrize("case", test_cases)
def test_login(api_client, case):
    response = api_client.post("/login", json=case["data"])
    assert response.status_code == case["expected_status"]

    response_data = response.json()

    for field in case["expected_fields"]:
        assert field in response_data

    if "token" in case["expected_fields"]:
        assert isinstance(response_data["token"], str)
        assert response_data["token"] != ""
