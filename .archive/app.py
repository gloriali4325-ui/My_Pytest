# app.py

import requests
import pytest

def get_weather(city):

    url = f"https://api.weather.com/{city}"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("API error")

    data = response.json()

    return data["temperature"]


def fake_get_success(url):

    class MockResponse:

        status_code = 200

        def json(self):
            return {"temperature": 25}

    return MockResponse()


def fake_get_fail(url):

    class MockResponse:

        status_code = 500

        def json(self):
            return {}

    return MockResponse()
def test_success(monkeypatch):

    monkeypatch.setattr(
        requests,
        "get",
        fake_get_success
    )

    assert get_weather("beijing") == 25


def test_fail(monkeypatch):

    monkeypatch.setattr(
        requests,
        "get",
        fake_get_fail
    )

    with pytest.raises(Exception):

        get_weather("beijing")

def get_weather_status(city):

    url = f"https://api.weather.com/{city}"

    response = requests.get(url)

    if response.status_code != 200:
        return "error"

    data = response.json()

    if data["temperature"] > 30:
        return "hot"

    return "normal"

def make_fake_get(status_code, temperature=None):
    def fake_get(url):
        class MockResponse:
            def __init__(self):
                self.status_code = status_code

            def json(self):
                if temperature is None:
                    return {}
                return {"temperature": temperature}

        return MockResponse()

    return fake_get

@pytest.mark.parametrize("status_code, temperature, expected",[
    (200, 25, "normal"), 
    (200, 35, "hot"), 
    (500, None, "error")])
def test_weather_status(monkeypatch, status_code, temperature, expected):

    monkeypatch.setattr(
        requests,
        "get",
        make_fake_get(status_code, temperature)
    )

    assert get_weather_status("beijing") == expected



def get_stock_price(symbol):
    url = f"https://api.example.com/stocks/{symbol}"
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    data = response.json()
    return data["price"]



def fake_get_stock_price(url,**kwargs):
    class MockResponse:
        def __init__(self, status_code, price=None):
            self.status_code = status_code
            self.price = price
        def json(self):
            if self.price is None:
                return {}
            return {"price": self.price}
    return MockResponse(100)

def test_get_stock_price_success(monkeypatch):
    monkeypatch.setattr(
        requests,
        "get",
        fake_get_stock_price
    )
    assert get_stock_price("AAPL") == 100

def test_get_stock_price_timeout(monkeypatch):
    def fake_get_timeout(url, timeout):
        raise requests.exceptions.Timeout("Timeout error")
    monkeypatch.setattr(
        requests,
        "get",
        fake_get_timeout
    )
    with pytest.raises(requests.exceptions.Timeout):
        get_stock_price("AAPL")

def test_get_stock_price_connection_error(monkeypatch): 
    def fake_get_connection_error(url, timeout):
        raise requests.exceptions.ConnectionError("Connection error")
    monkeypatch.setattr(
        requests,
        "get",
        fake_get_connection_error
    )
    with pytest.raises(requests.exceptions.ConnectionError):
        get_stock_price("AAPL") 
