import allure
import pytest
from tests.helpers import api_call_or_xfail
from src.utils.assertions import assert_item_structure


@pytest.mark.smoke
@pytest.mark.contract
def test_successful_request_with_valid_seller_id(postman_api):
    seller_id = 999999
    with allure.step(f"Запросить объявления продавца {seller_id}"):
        response = api_call_or_xfail(
            lambda: postman_api.get_seller_items_v1(seller_id),
            "Проверка /api/1/:sellerID/item недоступна",
        )

    with allure.step("Проверить статус ответа и структуру списка объявлений"):
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert response_data
        assert_item_structure(response_data[0])

    with allure.step("Проверить соответствие sellerId в ответе"):
        assert response_data[0].get("sellerId") == seller_id


@pytest.mark.regression
def test_successful_request_with_min_seller_id(postman_api):
    seller_id = 111111
    with allure.step(f"Запросить объявления продавца с минимальным sellerId {seller_id}"):
        response = api_call_or_xfail(
            lambda: postman_api.get_seller_items_v1(seller_id),
            "Проверка /api/1/:sellerID/item (min) недоступна",
        )

    with allure.step("Проверить корректный ответ сервера"):
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)

@pytest.mark.skip(reason="Bag - некорректный ответ сервера")
@pytest.mark.parametrize(
    "seller_id, expected_status, expected_error_message",
    [
        (1000000, 404, "Seller ID is out of valid range"),
        ("abc123", 404, "Invalid seller ID format"),
        (" ", 404, "Seller ID is required"),
        (8888888, 404, "Seller not found"),
    ]
)
def test_negative_requests_invalid_seller_id(seller_id, expected_status, expected_error_message, postman_api):
    with allure.step(f"Запросить объявления с невалидным sellerId: {seller_id!r}"):
        response = postman_api.get_seller_items_v1(seller_id)

    with allure.step(f"Проверить, что сервер вернул статус {expected_status}"):
        assert response.status_code == expected_status
