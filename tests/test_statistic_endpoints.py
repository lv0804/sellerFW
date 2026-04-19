import allure
import pytest

from tests.helpers import api_call_or_xfail
from src.utils.assertions import assert_statistics_structure


@pytest.mark.smoke
@pytest.mark.contract
def test_get_statistic_v1_success(postman_api):
    with allure.step("Запросить статистику через GET /api/1/statistic/{id}"):
        response = api_call_or_xfail(
            lambda: postman_api.get_statistic_v1("6359a483-dae8-4231-adc8-c71c5f1eb401"),
            "Проверка /api/1/statistic недоступна",
        )

    with allure.step("Проверить код ответа и структуру статистики v1"):
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data
        assert_statistics_structure(data[0])


@pytest.mark.smoke
@pytest.mark.contract
def test_get_statistic_v2_success(postman_api):
    with allure.step("Запросить статистику через GET /api/2/statistic/{id}"):
        response = api_call_or_xfail(
            lambda: postman_api.get_statistic_v2("6359a483-dae8-4231-adc8-c71c5f1eb401"),
            "Проверка /api/2/statistic недоступна",
        )

    with allure.step("Проверить код ответа и структуру статистики v2"):
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data
        assert_statistics_structure(data[0])
