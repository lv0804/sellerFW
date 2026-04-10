PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
ALLURE_RESULTS ?= allure-results

.PHONY: help test test-smoke test-regression allure clean-allure

help:
	@echo "Доступные команды:"
	@echo "  make test            - Запуск всех тестов с выгрузкой в Allure"
	@echo "  make test-smoke      - Запуск smoke тестов с выгрузкой в Allure"
	@echo "  make test-regression - Запуск regression тестов с выгрузкой в Allure"
	@echo "  make allure          - Открыть Allure-отчет (allure serve)"
	@echo "  make clean-allure    - Очистить папку allure-results"

test:
	$(PYTEST) --alluredir=$(ALLURE_RESULTS)

test-smoke:
	$(PYTEST) -m smoke --alluredir=$(ALLURE_RESULTS)

test-regression:
	$(PYTEST) -m regression --alluredir=$(ALLURE_RESULTS)

allure:
	@command -v allure >/dev/null 2>&1 || { \
		echo "Ошибка: allure CLI не найден. Установите через 'brew install allure'."; \
		exit 1; \
	}
	allure serve $(ALLURE_RESULTS)

clean-allure:
	rm -rf $(ALLURE_RESULTS)