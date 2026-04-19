import re

from tests.settings import get_ui_base_url


class ModerationPage:
    def __init__(self, page):
        self.page = page
        self.title = page.get_by_text("Модерация Авито")
        self.listings_link = page.get_by_role("link", name=re.compile("Объявления"))
        self.stats_link = page.get_by_role("link", name=re.compile("Статистика"))
        self.theme_toggle = page.get_by_role("button", name=re.compile("Темная|Светлая|Switch to"))

        self.search_label = page.get_by_text("Поиск по названию")
        self.price_range_label = page.get_by_text("Диапазон цен (₽)")
        self.price_from_input = page.locator('input[placeholder="От"]')
        self.price_to_input = page.locator('input[placeholder="До"]')
        self.urgent_toggle = page.get_by_text("🔥 Только срочные")
        self.reset_button = page.get_by_role("button", name="Сбросить")

        # Ищем контролы по их смысловым опциям, а не по позиции на странице.
        self.sort_field_select = page.locator("select:has(option:text-is('Цене'))")
        self.sort_direction_select = page.locator(
            "select:has(option:text-is('По возрастанию')):has(option:text-is('По убыванию'))"
        )
        self.category_select = page.locator("select:has(option:text-is('Электроника'))")

    def open(self):
        self.page.goto(get_ui_base_url(), wait_until="domcontentloaded", timeout=60_000)

    def set_price_filter(self, min_price: int, max_price: int):
        self.price_from_input.fill(str(min_price))
        self.price_to_input.fill(str(max_price))

    def sort_by_price_ascending(self):
        self.sort_field_select.select_option(label="Цене")
        self.sort_direction_select.select_option(label="По возрастанию")

    def sort_by_price_descending(self):
        self.sort_direction_select.select_option(label="По убыванию")

    def filter_by_category(self, category: str):
        self.category_select.select_option(label=category)

    def enable_urgent_only(self):
        self.urgent_toggle.click()

    def get_prices(self) -> list[int]:
        prices = []
        cards = self.page.locator("[data-testid='card']")
        for i in range(cards.count()):
            text = cards.nth(i).get_by_test_id("price").inner_text()
            prices.append(int(re.sub(r"\D", "", text)))
        return prices
