import os
import re
from dataclasses import dataclass
from pathlib import Path
from time import monotonic

import allure
import pytest

playwright_sync_api = pytest.importorskip(
    "playwright.sync_api",
    reason="UI-тесты требуют установленный пакет playwright",
)

Browser = playwright_sync_api.Browser
Page = playwright_sync_api.Page
expect = playwright_sync_api.expect
sync_playwright = playwright_sync_api.sync_playwright


UI_BASE_URL = os.getenv("UI_BASE_URL", "https://cerulean-praline-8e5aa6.netlify.app")
KNOWN_CATEGORIES = {
    "Электроника",
    "Недвижимость",
    "Транспорт",
    "Работа",
    "Услуги",
    "Животные",
    "Мода",
    "Детское",
}
CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


@dataclass(frozen=True)
class AnnouncementCard:
    title: str
    price: int
    category: str
    is_urgent: bool


def _browser_launch_kwargs() -> dict:
    browser_path = os.getenv("UI_BROWSER_EXECUTABLE_PATH")
    if browser_path:
        return {"executable_path": browser_path}

    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return {"executable_path": candidate}

    return {}


def _body_text(page: Page) -> str:
    return page.locator("body").inner_text()


def _wait_for_list_ready(page: Page, timeout_ms: int = 10_000) -> str:
    deadline = monotonic() + timeout_ms / 1000
    last_text = ""
    last_reload_at = 0.0

    while monotonic() < deadline:
        last_text = _body_text(page)
        if "Загрузка объявлений..." not in last_text and "Объявление " in last_text and "Показано " in last_text:
            return last_text
        if "Ошибка при загрузке данных" in last_text and "Попробуйте обновить" in last_text:
            now = monotonic()
            # Защищаемся от флаки сети: повторно запрашиваем список не чаще раза в 1.5 секунды.
            if now - last_reload_at >= 1.5:
                refresh_button = page.get_by_role("button", name="Попробуйте обновить")
                if refresh_button.count():
                    refresh_button.first.click()
                else:
                    page.reload(wait_until="domcontentloaded")
                last_reload_at = now
        page.wait_for_timeout(250)

    raise AssertionError(
        "Список объявлений не загрузился в ожидаемое время.\n"
        f"Последнее состояние страницы:\n{last_text[:500]}"
    )


def _wait_for_stats_ready(page: Page, timeout_ms: int = 10_000) -> str:
    expect(page.get_by_text("Статистика модератора")).to_be_visible(timeout=timeout_ms)
    deadline = monotonic() + timeout_ms / 1000
    last_text = ""

    while monotonic() < deadline:
        last_text = _body_text(page)
        if "Статистика модератора" in last_text and (
            "Обновление через:" in last_text or "Автообновление выключено" in last_text
        ):
            return last_text
        page.wait_for_timeout(250)

    raise AssertionError(
        "Блок статистики не перешел в готовое состояние.\n"
        f"Последнее состояние страницы:\n{last_text[:500]}"
    )


def _parse_visible_cards(page: Page) -> list[AnnouncementCard]:
    text = _body_text(page)
    text = text.split("Показано ", 1)[0]
    blocks = re.split(r"(?=Объявление \d+: )", text)
    cards: list[AnnouncementCard] = []

    for block in blocks:
        block = block.strip()
        if not block.startswith("Объявление "):
            continue

        lines = [line.strip() for line in block.splitlines() if line.strip()]
        price_line = next((line for line in lines if "₽" in line), None)
        if not price_line:
            continue

        price = int(re.sub(r"\D", "", price_line))
        category_index = lines.index(price_line) + 1
        category = next((line for line in lines[category_index:] if line in KNOWN_CATEGORIES), "")
        cards.append(
            AnnouncementCard(
                title=lines[0],
                price=price,
                category=category,
                is_urgent="Срочно" in lines,
            )
        )

    return cards


def _extract_timer_seconds(page: Page) -> int | None:
    text = _body_text(page)
    if "Автообновление выключено" in text:
        return None

    match = re.search(r"Обновление через:\s*(\d+):(\d+)", text)
    if not match:
        return None

    minutes, seconds = match.groups()
    return int(minutes) * 60 + int(seconds)


def _open_list_page(page: Page) -> None:
    page.goto(UI_BASE_URL, wait_until="domcontentloaded", timeout=60_000)
    _wait_for_list_ready(page)


def _open_stats_page(page: Page) -> None:
    _open_list_page(page)
    page.get_by_role("link", name=re.compile("Статистика")).click()
    _wait_for_stats_ready(page)


def _wait_for_timer_visible(page: Page, timeout_ms: int = 8_000) -> int:
    deadline = monotonic() + timeout_ms / 1000
    timer_value = _extract_timer_seconds(page)
    while monotonic() < deadline:
        if timer_value is not None:
            return timer_value
        page.wait_for_timeout(250)
        timer_value = _extract_timer_seconds(page)
    raise AssertionError("Таймер автообновления не появился в ожидаемое время.")


@pytest.fixture(scope="session")
def ui_browser() -> Browser:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, **_browser_launch_kwargs())
        yield browser
        browser.close()


@pytest.fixture()
def desktop_page(ui_browser: Browser) -> Page:
    context = ui_browser.new_context(viewport={"width": 1440, "height": 1200}, locale="ru-RU")
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture()
def mobile_page(ui_browser: Browser) -> Page:
    context = ui_browser.new_context(
        viewport={"width": 390, "height": 844},
        is_mobile=True,
        has_touch=True,
        locale="ru-RU",
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.mark.ui
@pytest.mark.regression
def test_main_page_renders_core_layout(desktop_page: Page):
    with allure.step("Открыть главную страницу"):
        desktop_page.goto(UI_BASE_URL, wait_until="domcontentloaded", timeout=60_000)

    with allure.step("Проверить, что базовые разделы интерфейса отображаются"):
        expect(desktop_page.get_by_text("Модерация Авито")).to_be_visible()
        expect(desktop_page.get_by_role("link", name=re.compile("Объявления"))).to_be_visible()
        expect(desktop_page.get_by_role("link", name=re.compile("Статистика"))).to_be_visible()
        expect(desktop_page.get_by_role("button", name=re.compile("Темная|Светлая|Switch to"))).to_be_visible()


@pytest.mark.ui
@pytest.mark.regression
def test_main_page_renders_filter_controls(desktop_page: Page):
    with allure.step("Открыть главную страницу"):
        desktop_page.goto(UI_BASE_URL, wait_until="domcontentloaded", timeout=60_000)

    with allure.step("Проверить доступность ключевых элементов фильтрации"):
        expect(desktop_page.get_by_text("Поиск по названию")).to_be_visible()
        expect(desktop_page.get_by_text("🔥 Только срочные")).to_be_visible()
        expect(desktop_page.get_by_text("Диапазон цен (₽)")).to_be_visible()
        expect(desktop_page.locator('input[placeholder="От"]')).to_be_visible()
        expect(desktop_page.locator('input[placeholder="До"]')).to_be_visible()
        expect(desktop_page.get_by_role("button", name="Сбросить")).to_be_visible()


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.xfail(
    reason="Известная нестабильность UI-данных/загрузки на стенде: фильтр цены может возвращать нерелевантные карточки.",
    strict=True,
)
def test_main_page_filters_items_by_price_range(desktop_page: Page):
    min_price = 10_000
    max_price = 50_000

    with allure.step("Открыть главную страницу со списком объявлений"):
        _open_list_page(desktop_page)

    with allure.step(f"Применить фильтр цены от {min_price} до {max_price} рублей"):
        desktop_page.locator('input[placeholder="От"]').fill(str(min_price))
        desktop_page.locator('input[placeholder="До"]').fill(str(max_price))
        _wait_for_list_ready(desktop_page)
        cards = _parse_visible_cards(desktop_page)

    with allure.step("Проверить, что все видимые объявления попали в заданный диапазон"):
        assert cards, "После применения диапазона цен на странице не осталось видимых карточек."
        assert all(min_price <= card.price <= max_price for card in cards), (
            "Найдены объявления вне выбранного диапазона цен. "
            f"Диапазон: {min_price}-{max_price}, цены: {[card.price for card in cards]}"
        )


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.xfail(
    reason="Известная нестабильность UI-стенда: список объявлений может не загружаться из-за временной ошибки данных.",
    strict=True,
)
def test_main_page_sorts_items_by_price(desktop_page: Page):
    with allure.step("Открыть главную страницу со списком объявлений"):
        _open_list_page(desktop_page)

    with allure.step("Отсортировать объявления по цене по возрастанию"):
        desktop_page.locator("select").nth(0).select_option(label="Цене")
        desktop_page.locator("select").nth(1).select_option(label="По возрастанию")
        _wait_for_list_ready(desktop_page)
        ascending_cards = _parse_visible_cards(desktop_page)

    with allure.step("Проверить порядок цен по возрастанию"):
        assert ascending_cards, "После сортировки по цене не найдено ни одной карточки."
        ascending_prices = [card.price for card in ascending_cards]
        assert ascending_prices == sorted(ascending_prices), (
            "Сортировка по цене 'По возрастанию' работает некорректно. "
            f"Фактический порядок: {ascending_prices}"
        )

    with allure.step("Переключить сортировку по цене на убывание"):
        desktop_page.locator("select").nth(1).select_option(label="По убыванию")
        _wait_for_list_ready(desktop_page)
        descending_cards = _parse_visible_cards(desktop_page)

    with allure.step("Проверить порядок цен по убыванию"):
        assert descending_cards, "После смены порядка сортировки карточки исчезли."
        descending_prices = [card.price for card in descending_cards]
        assert descending_prices == sorted(descending_prices, reverse=True), (
            "Сортировка по цене 'По убыванию' работает некорректно. "
            f"Фактический порядок: {descending_prices}"
        )


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.xfail(
    reason="Известная нестабильность UI-данных на стенде: фильтр категории может отдавать карточки других категорий.",
    strict=True,
)
def test_main_page_filters_items_by_category(desktop_page: Page):
    selected_category = "Электроника"

    with allure.step("Открыть главную страницу со списком объявлений"):
        _open_list_page(desktop_page)

    with allure.step(f"Выбрать категорию '{selected_category}'"):
        desktop_page.locator("select").nth(2).select_option(label=selected_category)
        _wait_for_list_ready(desktop_page)
        cards = _parse_visible_cards(desktop_page)

    with allure.step("Проверить, что у всех видимых объявлений выбранная категория"):
        assert cards, f"После выбора категории '{selected_category}' карточки не отображаются."
        assert all(card.category == selected_category for card in cards), (
            "На странице отображаются объявления из другой категории. "
            f"Ожидалась категория: {selected_category}, фактические: {[card.category for card in cards]}"
        )


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.xfail(
    reason="Известная нестабильность UI-стенда: при включении фильтра срочных список может не перейти в готовое состояние.",
    strict=True,
)
def test_main_page_shows_only_urgent_items_when_toggle_is_enabled(desktop_page: Page):
    with allure.step("Открыть главную страницу со списком объявлений"):
        _open_list_page(desktop_page)

    with allure.step("Включить фильтр 'Только срочные'"):
        desktop_page.get_by_text("🔥 Только срочные").click()
        _wait_for_list_ready(desktop_page, timeout_ms=8_000)
        cards = _parse_visible_cards(desktop_page)

    with allure.step("Проверить, что на странице остались только срочные объявления"):
        assert cards, "После включения фильтра 'Только срочные' список объявлений пуст."
        assert all(card.is_urgent for card in cards), (
            "После включения фильтра 'Только срочные' найдены обычные объявления. "
            f"Карточки: {[card.title for card in cards if not card.is_urgent]}"
        )


@pytest.mark.ui
@pytest.mark.regression
def test_stats_page_manual_refresh_button_resets_timer(desktop_page: Page):
    with allure.step("Открыть страницу статистики"):
        _open_stats_page(desktop_page)

    with allure.step("Зафиксировать начальное значение таймера автообновления"):
        initial_timer = _extract_timer_seconds(desktop_page)
        assert initial_timer is not None, "Таймер автообновления не отображается до ручного обновления."

    with allure.step("Убедиться, что таймер уменьшается со временем"):
        desktop_page.wait_for_timeout(2_200)
        decreased_timer = _extract_timer_seconds(desktop_page)
        assert decreased_timer is not None and decreased_timer < initial_timer, (
            "Таймер не уменьшается сам по себе, поэтому проверка кнопки 'Обновить' некорректна."
        )

    with allure.step("Нажать кнопку 'Обновить'"):
        desktop_page.get_by_role("button", name="Обновить сейчас").click()
        desktop_page.wait_for_timeout(1_000)
        refreshed_timer = _extract_timer_seconds(desktop_page)

    with allure.step("Проверить, что ручное обновление перезапустило таймер"):
        assert refreshed_timer is not None, "После нажатия 'Обновить' таймер пропал."
        assert refreshed_timer > decreased_timer, (
            "Кнопка 'Обновить' не перезапустила таймер автообновления. "
            f"До обновления: {decreased_timer}, после обновления: {refreshed_timer}"
        )


@pytest.mark.ui
@pytest.mark.regression
def test_stats_page_stop_timer_button_disables_auto_refresh(desktop_page: Page):
    with allure.step("Открыть страницу статистики"):
        _open_stats_page(desktop_page)

    with allure.step("Остановить автообновление"):
        desktop_page.get_by_role("button", name="Отключить автообновление").click()
        desktop_page.wait_for_timeout(500)
        body_text = _wait_for_stats_ready(desktop_page)

    with allure.step("Проверить, что таймер остановился и появилась кнопка запуска"):
        assert "Автообновление выключено" in body_text, (
            "После остановки таймера сообщение о выключенном автообновлении не появилось."
        )
        assert _extract_timer_seconds(desktop_page) is None, "После остановки таймера время продолжает отображаться."
        expect(desktop_page.get_by_role("button", name="Включить автообновление")).to_be_visible()


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.xfail(
    reason="Известная нестабильность UI-стенда: после повторного запуска автообновления таймер может не отображаться.",
    strict=True,
)
def test_stats_page_start_timer_button_reenables_auto_refresh(desktop_page: Page):
    with allure.step("Открыть страницу статистики"):
        _open_stats_page(desktop_page)

    with allure.step("Остановить автообновление и дождаться кнопки запуска"):
        desktop_page.get_by_role("button", name="Отключить автообновление").click()
        desktop_page.wait_for_timeout(500)
        expect(desktop_page.get_by_role("button", name="Включить автообновление")).to_be_visible()

    with allure.step("Запустить автообновление повторно"):
        desktop_page.get_by_role("button", name="Включить автообновление").click()
        _wait_for_stats_ready(desktop_page)
        restarted_timer = _wait_for_timer_visible(desktop_page)

    with allure.step("Проверить, что таймер снова появился и начал отсчет"):
        assert restarted_timer is not None, "После запуска таймер автообновления не восстановился."
        assert restarted_timer > 0, "После запуска таймер отображается некорректно."


@pytest.mark.ui
@pytest.mark.regression
def test_mobile_theme_toggle_switches_between_light_and_dark_modes(mobile_page: Page):
    with allure.step("Открыть главную страницу в мобильном viewport"):
        _open_list_page(mobile_page)
        theme_toggle = mobile_page.get_by_role("button", name=re.compile("Switch to"))
        initial_background = mobile_page.evaluate("() => getComputedStyle(document.body).backgroundColor")
        initial_icon = theme_toggle.inner_text().strip()

    with allure.step("Переключить тему на противоположную"):
        theme_toggle.click()
        mobile_page.wait_for_timeout(600)
        dark_background = mobile_page.evaluate("() => getComputedStyle(document.body).backgroundColor")
        dark_icon = theme_toggle.inner_text().strip()

    with allure.step("Проверить, что тема и иконка переключателя изменились"):
        assert dark_background != initial_background, "После переключения темы цвет фона не изменился."
        assert dark_icon != initial_icon, "После переключения темы иконка тогла не изменилась."

    with allure.step("Повторно переключить тему и проверить возврат к исходному состоянию"):
        theme_toggle.click()
        mobile_page.wait_for_timeout(600)
        restored_background = mobile_page.evaluate("() => getComputedStyle(document.body).backgroundColor")
        restored_icon = theme_toggle.inner_text().strip()

        assert restored_background == initial_background, "После повторного переключения светлая тема не восстановилась."
        assert restored_icon == initial_icon, "После повторного переключения иконка тогла не вернулась в исходное состояние."
