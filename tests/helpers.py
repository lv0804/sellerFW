import pytest
import requests


def api_call_or_xfail(api_call, reason: str):
    try:
        return api_call()
    except requests.exceptions.RequestException as error:
        pytest.xfail(f"{reason}. Сетевая ошибка стенда: {error}")
