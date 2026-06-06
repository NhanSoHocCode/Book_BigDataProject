from __future__ import annotations

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from book_crawler.items import BOOK_FIELDS


class NormalizeBookFieldsPipeline:
    """Keep crawler output aligned with the 17-column ETL schema."""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        normalized = {field: adapter.get(field) for field in BOOK_FIELDS}
        if not normalized["book_id"] and not normalized["url"]:
            raise DropItem("Missing both book_id and url")
        if not normalized["source"]:
            normalized["source"] = spider.name
        return normalized


class DropDuplicateBooksPipeline:
    def __init__(self) -> None:
        self.seen_keys: set[str] = set()

    def process_item(self, item, spider):
        key = f"{item.get('source') or spider.name}:{item.get('book_id') or item.get('url')}"
        if key in self.seen_keys:
            raise DropItem(f"Duplicate book: {key}")
        self.seen_keys.add(key)
        return item
