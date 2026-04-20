import pytest

@pytest.fixture
def number():
    return 10

def test_double(number):

    assert number * 2 == 20


@pytest.fixture
def x():

    return 3

@pytest.fixture
def y():

    return 4


def test_sum(x, y):

    assert x+y == 7



@pytest.fixture
def username():

    print("create username")

    return "admin"


def test_login(username):

    result = f"login:{username}"

    assert result == "login:admin"

@pytest.mark.smoke
def test_profile(username):

    result = f"profile:{username}"

    assert result == "profile:admin"


@pytest.fixture(params=['chrome', 'firefox', 'safari'],scope='module')
def browser(request):
    print(f"setup {request.param} browser")
    yield request.param
    print(f"teardown {request.param} browser")

def test_webbrowser(browser):
    print(f"testing {browser} browser")
