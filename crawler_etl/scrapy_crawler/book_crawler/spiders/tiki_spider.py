"""Scrapy spider for the Tiki public listing API."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urljoin

import scrapy

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from crawler_etl.scrapy_crawler.book_crawler.items import BookItem
from crawler_etl.scrapy_crawler.book_crawler.text_utils import fold_text


DEFAULT_CONFIG = PROJECT_ROOT / "crawler_etl" / "config" / "tiki_config.json"
ROOT_CATEGORY_NAMES = {"sách tiếng việt", "english books"}


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def first_author(item: dict[str, Any]) -> str | None:
    authors = item.get("authors") or []
    if isinstance(authors, list) and authors:
        author = authors[0]
        if isinstance(author, dict):
            return author.get("name")
        return str(author)
    return None


def compact_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def first_text(*values: Any) -> str | None:
    for value in values:
        text = compact_text(value)
        if text:
            return text
    return None


def normalized_text(value: Any) -> str | None:
    text = compact_text(value)
    return text.casefold() if text else None


def is_root_category(value: Any) -> bool:
    normalized = normalized_text(value)
    return normalized in ROOT_CATEGORY_NAMES if normalized else False


def first_non_root_text(*values: Any) -> str | None:
    for value in values:
        text = compact_text(value)
        if text and not is_root_category(text):
            return text
    return None


def badge_text(item: dict[str, Any], code: str) -> str | None:
    for badge in item.get("badges_new") or []:
        if isinstance(badge, dict) and badge.get("code") == code:
            return compact_text(badge.get("text"))
    return None


def author_name(item: dict[str, Any]) -> str | None:
    return first_text(
        item.get("author_name"),
        first_author(item),
        item.get("brand_name"),
        badge_text(item, "brand_name"),
    )


def item_url(item: dict[str, Any]) -> str | None:
    value = item.get("url_path") or item.get("url_key")
    if not value:
        return None
    return urljoin("https://tiki.vn/", str(value))


def sold_count(item: dict[str, Any]) -> int:
    quantity_sold = item.get("quantity_sold") or {}
    if isinstance(quantity_sold, dict):
        value = quantity_sold.get("value")
        if isinstance(value, int):
            return value
    return 0


def sub_category_name(item: dict[str, Any]) -> str | None:
    categories = item.get("categories") or {}
    if isinstance(categories, dict):
        return categories.get("name")
    return None


def amplitude_metadata(item: dict[str, Any]) -> dict[str, Any]:
    visible_info = item.get("visible_impression_info") or {}
    if not isinstance(visible_info, dict):
        return {}
    amplitude = visible_info.get("amplitude") or {}
    return amplitude if isinstance(amplitude, dict) else {}


def main_category_name(item: dict[str, Any], category: dict[str, Any]) -> str | None:
    amplitude = amplitude_metadata(item)
    if not category.get("is_root"):
        return first_non_root_text(
            category.get("main_category"),
            category.get("name"),
            amplitude.get("category_l3_name"),
            amplitude.get("category_l2_name"),
            sub_category_name(item),
        )

    return first_non_root_text(
        amplitude.get("category_l3_name"),
        amplitude.get("category_l2_name"),
        sub_category_name(item),
        amplitude.get("primary_category_name"),
        category.get("main_category"),
        category.get("name"),
    )


def sub_category_from_item(item: dict[str, Any], category: dict[str, Any]) -> str | None:
    amplitude = amplitude_metadata(item)
    return first_non_root_text(
        amplitude.get("primary_category_name"),
        sub_category_name(item),
        amplitude.get("category_l4_name"),
        amplitude.get("category_l3_name"),
        category.get("sub_category"),
        category.get("name"),
    )


def request_url(endpoint: str, params: dict[str, Any]) -> str:
    return f"{endpoint}?{urlencode(params)}"


def json_ld_name(value: Any) -> str | None:
    if isinstance(value, dict):
        return compact_text(value.get("name"))
    if isinstance(value, str):
        return compact_text(value)
    return None


def iter_json_ld_records(payload: Any):
    if isinstance(payload, list):
        for item in payload:
            yield from iter_json_ld_records(item)
    elif isinstance(payload, dict):
        yield payload
        graph = payload.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                yield from iter_json_ld_records(item)


def tiki_json_ld_product(response) -> dict[str, Any]:
    for script_text in response.css('script[type="application/ld+json"]::text').getall():
        try:
            payload = json.loads(script_text.strip())
        except json.JSONDecodeError:
            continue

        for record in iter_json_ld_records(payload):
            record_type = record.get("@type")
            types = record_type if isinstance(record_type, list) else [record_type]

            if "Product" in types:
                return record

    return {}

def tiki_json_ld_metadata(response) -> dict[str, str]:
    metadata: dict[str, str] = {}

    product = tiki_json_ld_product(response)
    properties = product.get("additionalProperty") or product.get("additionalProperties") or []

    if isinstance(properties, dict):
        properties = [properties]

    for prop in properties:
        if not isinstance(prop, dict):
            continue

        name = compact_text(prop.get("name"))
        value = compact_text(prop.get("value"))

        if name and value:
            metadata[name.casefold()] = value

    return metadata

class TikiSpider(scrapy.Spider):
    name = "tiki"
    allowed_domains = ["tiki.vn"]

    def __init__(self, config: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.config_path = Path(config) if config else DEFAULT_CONFIG
        self.config_data = load_config(self.config_path)
        self.max_pages = int(self.config_data.get("max_pages", 1))
        self.max_items = int(self.config_data.get("max_items", 0))
        self.crawl_detail_html = bool(self.config_data.get("crawl_detail_html", False))
        self.max_detail_requests = int(self.config_data.get("max_detail_requests", 0))
        self.detail_requests = 0
        self.discover_categories = bool(self.config_data.get("discover_categories", False))
        self.crawl_root_categories = bool(self.config_data.get("crawl_root_categories", True))
        self.max_discovered_categories = int(self.config_data.get("max_discovered_categories", 0))
        self.items_yielded = 0
        self.discovered_categories = 0
        self.seen_category_ids: set[str] = set()
        self.seen_keys: set[str] = set()

    def start_requests(self):
        for category in self.config_data.get("categories", []):
            category_id = str(category["category_id"])
            self.seen_category_ids.add(category_id)
            yield self.build_listing_request({**category, "is_root": True}, page=1)

    def build_listing_request(self, category: dict[str, Any], page: int):
        params = {
            **self.config_data.get("extra_params", {}),
            "limit": self.config_data.get("limit", 40),
            "page": page,
            "category": category["category_id"],
            "urlKey": category.get("url_key") or category["category_id"],
        }
        return scrapy.Request(
            url=request_url(self.config_data["endpoint"], params),
            callback=self.parse_listing,
            cb_kwargs={"category": category, "page": page},
        )

    def parse_listing(self, response, category: dict[str, Any], page: int):
        if self.max_items and self.items_yielded >= self.max_items:
            return

        try:
            payload = response.json()
        except json.JSONDecodeError:
            self.logger.warning("Skip non-JSON Tiki response: %s", response.url)
            return

        items = payload.get("data") or []
        is_root_category = bool(category.get("is_root"))

        if self.discover_categories and is_root_category and page == 1:
            discovered_requests = list(self.discover_child_categories(payload, category))
            if discovered_requests:
                self.logger.info(
                    "Discovered %s child Tiki categories from %s",
                    len(discovered_requests),
                    category.get("name"),
                )
                yield from discovered_requests
            else:
                self.logger.warning(
                    "No child Tiki categories discovered from %s; crawling root category.",
                    category.get("name"),
                )

        if self.discover_categories and is_root_category and not self.crawl_root_categories:
            return

        if not items:
            return

        for raw_item in items:
            if self.max_items and self.items_yielded >= self.max_items:
                return
            if not isinstance(raw_item, dict):
                continue

            book_id = raw_item.get("id") or raw_item.get("sku")
            url = item_url(raw_item)
            dedupe_key = f"tiki:{book_id or url}"
            if dedupe_key in self.seen_keys:
                continue
            self.seen_keys.add(dedupe_key)
            self.items_yielded += 1

            item = BookItem(
                book_id=book_id,
                source="tiki",
                title=raw_item.get("name"),
                author=author_name(raw_item),
                publisher=None,
                language_group=category.get("language_group"),
                main_category=main_category_name(raw_item, category),
                sub_category=sub_category_from_item(raw_item, category),
                price=raw_item.get("price"),
                original_price=raw_item.get("original_price"),
                discount_rate=raw_item.get("discount_rate"),
                rating=raw_item.get("rating_average"),
                review_count=raw_item.get("review_count"),
                sold_count=sold_count(raw_item),
                publish_year=None,
                page_count=None,
                url=url,
            )

            if (
                self.crawl_detail_html
                and url
                and (not self.max_detail_requests or self.detail_requests < self.max_detail_requests)
            ):
                self.detail_requests += 1
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_detail_html,
                    cb_kwargs={"item": item},
                    priority=1,
                )
            else:
                yield item

        if page < self.max_pages:
            yield self.build_listing_request(category, page=page + 1)

    def discover_child_categories(self, payload: dict[str, Any], parent_category: dict[str, Any]):
        for filter_item in payload.get("filters") or []:
            if not isinstance(filter_item, dict):
                continue
            if filter_item.get("code") != "category" and filter_item.get("query_name") != "category":
                continue

            for value in filter_item.get("values") or []:
                if not isinstance(value, dict):
                    continue
                if self.max_discovered_categories and self.discovered_categories >= self.max_discovered_categories:
                    return

                category_id = value.get("query_value")
                if category_id is None:
                    continue

                category_id = str(category_id)
                if category_id in self.seen_category_ids:
                    continue

                category_name = first_text(value.get("display_value"), parent_category.get("name"))
                if not category_name:
                    continue

                self.seen_category_ids.add(category_id)
                self.discovered_categories += 1
                yield self.build_listing_request(
                    {
                        "name": category_name,
                        "main_category": category_name,
                        "sub_category": category_name,
                        "language_group": parent_category.get("language_group"),
                        "category_id": category_id,
                        "url_key": value.get("url_key") or category_id,
                    },
                    page=1,
                )

    def parse_detail_html(self, response, item: BookItem):
        metadata = tiki_json_ld_metadata(response)

        publisher = metadata.get("nhà xuất bản")
        page_count = metadata.get("số trang")
        publish_year = metadata.get("năm xuất bản") or metadata.get("năm xb")

        product = tiki_json_ld_product(response)
        if not publisher:
            publisher = json_ld_name(product.get("manufacturer")) or json_ld_name(product.get("brand"))

        if publisher:
            item["publisher"] = publisher
        if publish_year:
            item["publish_year"] = publish_year
        if page_count:
            item["page_count"] = page_count

        yield item