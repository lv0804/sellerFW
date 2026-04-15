PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
PLAYWRIGHT ?= $(PYTHON) -m playwright
ALLURE_RESULTS ?= allure-results

.PHONY: help test test-smoke test-regression test-ui install-browser allure clean-allure

help:
	@echo "Доступные команды:"
	@echo "  make test            - Запуск всех тестов с выгрузкой в Allure"
	@echo "  make test-smoke      - Запуск smoke тестов с выгрузкой в Allure"
	@echo "  make test-regression - Запуск regression тестов с выгрузкой в Allure"
	@echo "  make test-ui         - Запуск UI-тестов задания 2.2"
	@echo "  make install-browser - Установка Playwright Chromium"
	@echo "  make allure          - Открыть Allure-отчет (allure serve)"
	@echo "  make clean-allure    - Очистить папку allure-results"

test:
	$(PYTEST) --alluredir=$(ALLURE_RESULTS)

test-smoke:
	$(PYTEST) -m smoke --alluredir=$(ALLURE_RESULTS)

test-regression:
	$(PYTEST) -m "regression and not ui" --alluredir=$(ALLURE_RESULTS)

test-ui:
	$(PYTEST) tests/test_ui_moderation_platform.py --alluredir=$(ALLURE_RESULTS)

install-browser:
	$(PLAYWRIGHT) install chromium

allure:
	@command -v allure >/dev/null 2>&1 || { \
		echo "Ошибка: allure CLI не найден. Установите через 'brew install allure'."; \
		exit 1; \
	}
	allure serve $(ALLURE_RESULTS)

clean-allure:
	rm -rf $(ALLURE_RESULTS)