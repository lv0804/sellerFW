import pytest
from tests.helpers import api_call_or_xfail


@pytest.mark.smoke
@pytest.mark.contract
def test_create_item_v1_success(postman_api, build_item_payload):
    response = api_call_or_xfail(
        lambda: postman_api.create_item_v1(build_item_payload()),
        "Проверка POST /api/1/item недоступна",
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data or "id" in data


@pytest.mark.regression
@pytest.mark.contract
def test_create_item_v1_empty_body(postman_api):
    response = api_call_or_xfail(
        lambda: postman_api.create_item_v1({}),
        "Проверка POST /api/1/item с пустым body недоступна",
    )
    assert response.status_code == 400