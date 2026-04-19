import allure
import pytest
import re
import time
from tests.helpers import api_call_or_xfail
from src.utils.assertions import assert_item_structure

@pytest.mark.smoke
@pytest.mark.contract
def test_successful_request_with_valid_id(postman_api, build_item_payload):
    with allure.step("Создать объявление через POST /api/1/item"):
        create_response = api_call_or_xfail(
            lambda: postman_api.create_item_v1(build_item_payload()),
            "Подготовка данных для /api/1/item/:id недоступна",
        )
        assert create_response.status_code == 200

    with allure.step("Извлечь id созданного объявления из ответа"):
        create_data = create_response.json()
        created_item_id = create_data.get("id")
        if not created_item_id:
            # API иногда возвращает идентификатор только в поле status:
            # "Сохранили объявление - <uuid>"
            status_text = create_data.get("status", "")
            match = re.search(
                r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
                status_text,
            )
            created_item_id = match.group(0) if match else None

        assert isinstance(created_item_id, str)

    with allure.step("Получить объявление по id через GET /api/1/item/{id}"):
        response = None
        for attempt in range(5):
            response = api_call_or_xfail(
                lambda: postman_api.get_item_v1(created_item_id),
                "Проверка /api/1/item/:id недоступна",
            )
            if response.status_code == 200:
                break
            if response.status_code != 404:
                break
            if attempt < 4:
                time.sleep(1)

    with allure.step("Проверить код ответа и структуру элемента"):
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data
        assert_item_structure(data[0])

@pytest.mark.regression
@pytest.mark.parametrize("id, expected_status_code", [
    ("999", 400),
    (" ", 400),
    (999, 400)
])
def test_negative_requests_with_invalid_id(id, expected_status_code, postman_api):
    with allure.step(f"Запросить объявление с невалидным id: {id!r}"):
        response = api_call_or_xfail(
            lambda: postman_api.get_item_v1(id),
            "Проверка негативного сценария /api/1/item/:id недоступна",
        )

    with allure.step(f"Проверить, что сервер вернул статус {expected_status_code}"):
        assert response.status_code == expected_status_code

