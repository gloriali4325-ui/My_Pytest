import requests


class APIClient:

    def __init__(self, base_url):
        self.base_url = base_url

    def build_url(self, path):
        return f"{self.base_url}{path}"

    # ⭐ 核心方法
    def request(self, method, path, json=None):
        url = self.build_url(path)

        response = requests.request(
            method=method,
            url=url,
            json=json,
            timeout=5
        )

        return response

    # ⭐ 包装 POST
    def post(self, path, json=None):
        return self.request(
            "POST",
            path,
            json=json
        )

    # ⭐ 包装 GET（后面一定会用到）
    def get(self, path, params=None):

        url = self.build_url(path)

        response = requests.get(
            url=url,
            params=params
        )

        return response