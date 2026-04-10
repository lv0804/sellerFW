from typing import Any

from src.core.http_client import HttpClient


class PostmanApi:
    def __init__(self, client: HttpClient):
        self.client = client

    # API v1
    def get_item_v1(self, item_id: str | int):
        return self.client.get(f"/api/1/item/{item_id}")

    def create_item_v1(self, payload: dict[str, Any]):
        return self.client.post("/api/1/item", json=payload)

    def get_statistic_v1(self, item_id: str | int):
        return self.client.get(f"/api/1/statistic/{item_id}")

    def get_seller_items_v1(self, seller_id: str | int):
        return self.client.get(f"/api/1/{seller_id}/item")

    # API v2
    def delete_item_v2(self, item_id: str | int):
        return self.client.delete(f"/api/2/item/{item_id}")

    def get_statistic_v2(self, item_id: str | int):
        return self.client.get(f"/api/2/statistic/{item_id}")
