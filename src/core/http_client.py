from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class HttpClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        retries = Retry(
            total=2,
            connect=2,
            read=2,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "DELETE"]),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def close(self) -> None:
        self.session.close()

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.session.get(
            f"{self.base_url}{path}",
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs,
        )

    def post(self, path: str, json: dict[str, Any], **kwargs: Any) -> requests.Response:
        return self.session.post(
            f"{self.base_url}{path}",
            json=json,
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs,
        )

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.session.delete(
            f"{self.base_url}{path}",
            timeout=kwargs.pop("timeout", self.timeout),
            **kwargs,
        )
