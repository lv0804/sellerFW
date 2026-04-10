# sellerFW

API-автотесты на `pytest` с маркерами `smoke`, `regression` и поддержкой Allure.

## Быстрый старт

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
python3 -m pytest -m smoke --alluredir=allure-results
```

Если нужен HTML-отчет Allure:

```bash
brew install allure
allure serve allure-results
```

## Что нужно для запуска

- Python 3.10+; лучше 3.12
- `pip`
- `pytest`, `requests`, `allure-pytest` ставятся из `requirements.txt`
- `allure` CLI нужен только для открытия HTML-отчета
- `make` опционален, но удобен

## Подготовка окружения

Из корня проекта выполните:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Если виртуальное окружение уже создано:

```bash
source .venv/bin/activate
```

## Базовый URL

По умолчанию тесты используют:

```bash
https://qa-internship.avito.com
```

Если нужно запустить тесты на другом стенде:

```bash
export BASE_URL="https://your-stand.example.com"
```

Проверка текущего значения:

```bash
echo $BASE_URL
```

## Запуск тестов через pytest

Все тесты:

```bash
python3 -m pytest --alluredir=allure-results
```

Только `smoke`:

```bash
python3 -m pytest -m smoke --alluredir=allure-results
```

Только `regression`:

```bash
python3 -m pytest -m regression --alluredir=allure-results
```

Один файл:

```bash
python3 -m pytest tests/test_suit_get_items_by_ID.py --alluredir=allure-results
```

Один конкретный тест:

```bash
python3 -m pytest tests/test_suit_get_items_by_ID.py::test_successful_request_with_valid_id --alluredir=allure-results
```

Более подробный вывод:

```bash
python3 -m pytest -v --alluredir=allure-results
```

## Запуск через Makefile

Посмотреть все доступные команды:

```bash
make help
```

Основные команды:

```bash
make test
make test-smoke
make test-regression
make allure
make clean-allure
```

Назначение команд:

- `make test` запускает все тесты и сохраняет результаты в `allure-results`
- `make test-smoke` запускает только `smoke`
- `make test-regression` запускает только `regression`
- `make allure` открывает Allure-отчет
- `make clean-allure` удаляет папку `allure-results`

## Как работает Allure

Важно: флаг `--alluredir=allure-results` только сохраняет результаты тестов. Он не открывает отчет автоматически.

Обычный сценарий такой:

1. Запустить тесты:

```bash
python3 -m pytest -m smoke --alluredir=allure-results
```

2. Открыть отчет:

```bash
allure serve allure-results
```

Если команда `allure` не найдена, установите CLI:

```bash
brew install allure
```

Проверка установки:

```bash
allure --version
```

## Как читать результат pytest

Пример:

```text
7 passed, 9 deselected, 1 skipped
```

Что означает каждый статус:

- `passed` — тест прошел
- `failed` — тест упал
- `skipped` — тест пропущен
- `deselected` — тест найден, но не запущен из-за фильтра, например `-m smoke`
- `xfailed` — ожидаемое падение для теста, помеченного `xfail`
- `xpassed` — тест был помечен `xfail`, но неожиданно прошел

Пример с фильтром:

- команда `python3 -m pytest -m smoke --alluredir=allure-results`
- если всего в проекте 18 тестов, а `smoke` только 5, то pytest покажет `13 deselected`

Это не ошибка. Это значит, что остальные тесты были отфильтрованы и не запускались.

## Рекомендуемые команды

Быстрая проверка перед изменениями:

```bash
python3 -m pytest -m smoke --alluredir=allure-results
```

Полный регрессионный прогон:

```bash
python3 -m pytest -m regression --alluredir=allure-results
```

Полная проверка проекта:

```bash
python3 -m pytest --alluredir=allure-results
```

## Частые проблемы

### `command not found: allure`

У вас не установлен Allure CLI или он не находится в `PATH`.

Решение:

```bash
brew install allure
allure --version
```

### `No module named pytest`

Не активировано виртуальное окружение или не установлены зависимости.

Решение:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Ошибка сети или стенд недоступен

Проверьте:

- интернет
- VPN/прокси
- значение `BASE_URL`
- доступность стенда

### Почему тесты не все запускаются

Если вы используете:

```bash
python3 -m pytest -m smoke
```

то будут запущены только тесты с маркером `smoke`. Остальные попадут в `deselected`.