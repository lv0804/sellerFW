import allure
import pytest
from tests.helpers import api_call_or_xfail


@pytest.mark.smoke
@pytest.mark.contract
def test_create_item_v1_success(postman_api, build_item_payload):
    with allure.step("Создать объявление через POST /api/1/item"):
        response = api_call_or_xfail(
            lambda: postman_api.create_item_v1(build_item_payload()),
            "Проверка POST /api/1/item недоступна",
        )

    with allure.step("Проверить успешный статус и тело ответа"):
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "id" in data


@pytest.mark.regression
@pytest.mark.contract
def test_create_item_v1_empty_body(postman_api):
    with allure.step("Отправить POST /api/1/item с пустым body"):
        response = api_call_or_xfail(
            lambda: postman_api.create_item_v1({}),
            "Проверка POST /api/1/item с пустым body недоступна",
        )

    with allure.step("Проверить, что сервер вернул 400"):
        assert response.status_code == 400