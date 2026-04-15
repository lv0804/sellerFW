# sellerFW

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

При необходимости можно переопределить адрес стенда:

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