import pytest

from src.api.postman_api import PostmanApi
from src.core.http_client import HttpClient
from src.core.settings import get_base_url


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if hasattr(config.option, "allure_report_dir") and not config.option.allure_report_dir:
        config.option.allure_report_dir = "allure-results"


@pytest.fixture(scope="session")
def base_url():
    return get_base_url()


@pytest.fixture(scope="session")
def http_client(base_url):
    client = HttpClient(base_url=base_url)
    yield client
    client.close()


@pytest.fixture(scope="session")
def postman_api(http_client):
    return PostmanApi(client=http_client)


@pytest.fixture()
def item_payload():
    return {
        "name": "Телефон",
        "price": 85566,
        "sellerId": 999999,
        "statistics": {
            "contacts": 7,
            "likes": 5,
            "viewCount": 1,
        },
    }


@pytest.fixture()
def build_item_payload(item_payload: dict):
    def _builder(**overrides):
        payload = {
            **item_payload,
            "statistics": dict(item_payload["statistics"]),
        }
        for key, value in overrides.items():
            payload[key] = value
        return payload

    return _builder
