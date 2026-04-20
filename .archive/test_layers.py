import pytest


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def build_url(self, path):
        return self.base_url + path


@pytest.fixture(scope="session")
def config():
    return {"base_url": "https://test.api.com"}


@pytest.fixture(scope="session")
def api_client(config):
    return APIClient(base_url=config["base_url"])


@pytest.fixture(scope="module")
def auth_token(api_client):
    return "fake-token"


@pytest.fixture(scope="function")
def create_user(api_client, auth_token):
    user_id = "user-001"
    print(f"Using token: {auth_token}")
    print(f"Creating user at: {api_client.build_url('/users')} with ID: {user_id}")

    yield user_id

    print(f"Cleaning up user with ID: {user_id}")


def test_get_user(create_user):
    assert create_user == "user-001"

def build_prompt(api_name):
    return f"Generate pytest test for {api_name}"
print(build_prompt("get_user API"))