import pytest

test_cases = [
    {
        "name": "valid_email_password",
        "data": {
            "email": "test@example.com",
            "password": "securepassword123"
        },
        "expected_status": 200,
        "expected_fields": [
            "user_id"
        ]
    },
    {
        "name": "missing_email",
        "data": {
            "email": "",
            "password": "securepassword123"
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    },
    {
        "name": "missing_password",
        "data": {
            "email": "test@example.com",
            "password": ""
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    },
    {
        "name": "invalid_email",
        "data": {
            "email": "invalidemail",
            "password": "securepassword123"
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    },
    {
        "name": "valid_empty_password",
        "data": {
            "email": "test@example.com",
            "password": ""
        },
        "expected_status": 400,
        "expected_fields": [
            "error"
        ]
    }
]

@pytest.mark.parametrize("case", test_cases)
def test_register(api_client, case):
    response = api_client.post("/register", json=case["data"])
    assert response.status_code == case["expected_status"]

    response_data = response.json()

    for field in case["expected_fields"]:
        assert field in response_data

    if "user_id" in case["expected_fields"]:
        assert isinstance(response_data["user_id"], int)
        assert response_data["user_id"] >= 0
