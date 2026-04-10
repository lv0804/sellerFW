import pytest
import re
from tests.helpers import api_call_or_xfail


@pytest.mark.regression
@pytest.mark.contract
def test_delete_item_v2_success(postman_api, build_item_payload):
    create_response = api_call_or_xfail(
        lambda: postman_api.create_item_v1(build_item_payload()),
        "Подготовка данных для DELETE /api/2/item/:id недоступна",
    )
    assert create_response.status_code == 200
    create_data = create_response.json()
    created_item_id = create_data.get("id")
    if not created_item_id:
        status_text = create_data.get("status", "")
        match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            status_text,
        )
        created_item_id = match.group(0) if match else None
    assert isinstance(created_item_id, str)

    response = api_call_or_xfail(
        lambda: postman_api.delete_item_v2(created_item_id),
        "Проверка DELETE /api/2/item/:id недоступна",
    )
    assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.parametrize("invalid_id", ["", " ", "invalid-id"])
def test_delete_item_v2_invalid_id(postman_api, invalid_id):
    response = api_call_or_xfail(
        lambda: postman_api.delete_item_v2(invalid_id),
        "Проверка негативного DELETE /api/2/item/:id недоступна",
    )
    assert response.status_code in (400, 404)
