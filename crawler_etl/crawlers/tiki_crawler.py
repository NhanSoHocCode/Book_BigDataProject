"""Crawl book listings from the public Tiki JSON API."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "crawler_etl" / "config" / "tiki_config.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw" / "tiki_books.json"


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


def extract_book(item: dict[str, Any], category: dict[str, Any]) -> dict[str, Any]:
    quantity_sold = item.get("quantity_sold") or {}
    categories = item.get("categories") or {}
    sub_category = categories.get("name") if isinstance(categories, dict) else None
    return {
        "book_id": item.get("id") or item.get("sku"),
        "source": "tiki",
        "title": item.get("name"),
        "author": first_author(item),
        "publisher": None,
        "language_group": category.get("language_group"),
        "main_category": category.get("name"),
        "sub_category": sub_category or category.get("name"),
        "price": item.get("price"),
        "original_price": item.get("original_price"),
        "discount_rate": item.get("discount_rate"),
        "rating": item.get("rating_average"),
        "review_count": item.get("review_count"),
        "sold_count": quantity_sold.get("value") if isinstance(quantity_sold, dict) else 0,
        "publish_year": None,
        "page_count": None,
        "url": item.get("url_path") or item.get("url_key"),
    }


def crawl(config: dict[str, Any]) -> list[dict[str, Any]]:
    session = requests.Session()
    session.headers.update({"User-Agent": "BookBigDataSystem/1.0"})
    books: list[dict[str, Any]] = []
    for category in config["categories"]:
        for page in range(1, int(config["max_pages"]) + 1):
            params = {
                "limit": config["limit"],
                "page": page,
                "category": category["category_id"],
                "urlKey": category["category_id"],
            }
            response = session.get(
                config["endpoint"],
                params=params,
                timeout=config["timeout_seconds"],
            )
            response.raise_for_status()
            items = response.json().get("data") or []
            if not items:
                break
            books.extend(extract_book(item, category) for item in items)
            time.sleep(float(config["request_delay_seconds"]))
    return books


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    books = crawl(load_config(args.config))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False, indent=2)
    print(f"Wrote {len(books)} Tiki books to {args.output}")


if __name__ == "__main__":
    main()
