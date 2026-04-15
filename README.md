# sellerFW

API-автотесты на `pytest` с маркерами `smoke`, `regression` и поддержкой Allure +
UI-автотесты для задания 2.2 написаны на `pytest` + `Playwright`.  
Целевой стенд: [cerulean-praline-8e5aa6.netlify.app](https://cerulean-praline-8e5aa6.netlify.app/).

## Быстрый запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
make test-ui
```
## Что нужно для запуска

- Python 3.10+; лучше 3.12
- `pip`
- `pytest`, `requests`, `allure-pytest` ставятся из `requirements.txt`
- `allure` CLI нужен только для открытия HTML-отчета
- `make` опционален, но удобен

Если на машине нет установленного Chrome/Chromium, один раз поставьте браузер Playwright:

```bash
make install-browser
```

## Что запускается

Команда `make test-ui` запускает файл `tests/test_ui_moderation_platform.py`, который покрывает:

- фильтр `Диапазон цен`
- сортировку `По цене`
- фильтр `Категория`
- тогл `Только срочные`
- кнопки `Обновить`, `Остановить таймер`, `Запустить таймер` на странице статистики
- переключение светлой и тёмной темы на мобильном viewport

Все проверки содержат `assertions`.  
Если в приложении есть баг, тест падает по фактическому дефекту, а не из-за сломанной логики теста.

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


## Полезные команды

```bash
make help
make test-ui
make install-browser
make allure
make clean-allure
```

Запуск напрямую через `pytest`:

```bash
python3 -m pytest tests/test_ui_moderation_platform.py --alluredir=allure-results
```

## Переменные окружения

По умолчанию UI-тесты используют:

```bash
https://cerulean-praline-8e5aa6.netlify.app
```
По умолчанию API тесты используют:

```bash
https://qa-internship.avito.com
```

Если нужно запустить тесты на другом API стенде:

```bash
export BASE_URL="https://your-stand.example.com"

При необходимости можно переопределить адрес UI стенда:

```bash
export UI_BASE_URL="https://your-stand.example.com"
```

Если нужно явно указать браузерный бинарник:

```bash
export UI_BROWSER_EXECUTABLE_PATH="/path/to/browser"
```

## Отчет

Результаты `pytest` сохраняются в `allure-results`.

Чтобы открыть Allure-отчет:

```bash
brew install allure
allure serve allure-results
```

## Примечание по воспроизводимости

Стенд общий для всех кандидатов, поэтому тесты не опираются на:

- фиксированное количество карточек
- конкретные ID объявлений
- неизменность данных между прогонами

Проверки выполняются по текущим видимым объявлениям и состояниям интерфейса.