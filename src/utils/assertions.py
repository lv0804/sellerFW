from typing import Any


def assert_item_structure(item: dict[str, Any]) -> None:
    assert isinstance(item.get("id"), str)
    assert isinstance(item.get("sellerId"), int)
    assert isinstance(item.get("name"), str)
    assert isinstance(item.get("price"), int)

    statistics = item.get("statistics")
    assert isinstance(statistics, dict)
    assert isinstance(statistics.get("likes"), int)
    assert isinstance(statistics.get("viewCount"), int)
    assert isinstance(statistics.get("contacts"), int)


def assert_statistics_structure(stats: dict[str, Any]) -> None:
    assert isinstance(stats.get("likes"), int)
    assert isinstance(stats.get("viewCount"), int)
    assert isinstance(stats.get("contacts"), int)
