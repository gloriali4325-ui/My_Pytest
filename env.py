import os

def get_base_url():
    env = os.getenv("APP_ENV", "dev")

    if env == "prod":
        return "https://prod.api.com"
    elif env == "test":
        return "https://test.api.com"
    return "https://dev.api.com"


def read_config():
    with open("config.txt") as f:
        return f.read().strip()
    
def send_email(email_client, user):

    email_client.send(
        to=user,
        subject="Welcome",
        body="Hello!"
    )

