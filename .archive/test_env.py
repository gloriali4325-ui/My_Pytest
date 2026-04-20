from env import get_base_url
from env import read_config
import requests
import pytest
from env import send_email
from unittest.mock import MagicMock
from unittest.mock import patch


def test_get_prod_url(monkeypatch):
    monkeypatch.setenv("APP_ENV", "prod")

    assert get_base_url() == "https://prod.api.com"

def test_get_test_url(monkeypatch):
    
    monkeypatch.setenv("APP_ENV", "test")
    
    assert get_base_url() == "https://test.api.com" 

def test_get_dev_url(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    assert get_base_url() == "https://dev.api.com"


@pytest.mark.parametrize("env, expected_url", [
    ("prod", "https://prod.api.com"),
    ("test", "https://test.api.com"),
    ("", "https://dev.api.com")])
def test_get_base_url(monkeypatch, env, expected_url):
    if env:
        monkeypatch.setenv("APP_ENV", env)
    else:
        monkeypatch.delenv("APP_ENV", raising=False)

    assert get_base_url() == expected_url

def test_read_config(monkeypatch,tmp_path):
    config_file = tmp_path / "config.txt"
    config_file.write_text("hello_config")

    with monkeypatch.context() as m:
        m.chdir(tmp_path)
        assert read_config() == "hello_config"

def test_send_email():
    class MockEmailClient:
        def __init__(self):
            self.send = MagicMock()

    mock = MockEmailClient()

    send_email(mock, "alice@example.com")
    mock.send.assert_called_once_with(
        to="alice@example.com",
        subject="Welcome",
        body="Hello!"
    )
  
def fetch_user():

    response = requests.get("https://api.com/user")

    return response.json()["name"]

def test_fetch_user():
    with patch("app.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"name": "mock_user"}
        assert fetch_user() == "mock_user"
        
def fetch_user_with_retry():

    for _ in range(3):

        try:

            response = requests.get("https://api.com/user")

            return response.json()["name"]

        except requests.exceptions.Timeout:

            continue

    raise Exception("API failed")


def test_fetch_user_with_retry_twice():
    with patch("app.requests.get") as mock_get:
        mock_get.side_effect = [requests.exceptions.Timeout, requests.exceptions.Timeout, MagicMock(json=lambda: {"name": "mock_user"})]
        mock_get.return_value.json.return_value = {"name": "mock_user"}
        assert fetch_user_with_retry() == "mock_user"

def test_fetch_user_with_retry_fail():
    with patch("app.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout
        with pytest.raises(Exception, match="API failed"):
            fetch_user_with_retry()

def process_order(payment_service, order_id, amount):
    payment_service.pay(order_id=order_id, amount=amount)

def test_process_order():
    mock_payment_service = MagicMock()
    process_order(mock_payment_service, order_id="ORD001", amount=99.9)
    
    mock_payment_service.pay.assert_called_once_with(order_id="ORD001", amount=99.9)

def notify_users(email_client):

    email_client.send("alice@example.com")

    email_client.send("bob@example.com")
from unittest.mock import call


   
def test_notify_users():
    mock_email_client = MagicMock()
    notify_users(mock_email_client)
    assert mock_email_client.send.call_count==2
    mock_email_client.send.assert_has_calls([
         call("alice@example.com"),
    call("bob@example.com"),
])
    
