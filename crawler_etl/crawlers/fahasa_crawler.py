"""Crawl Fahasa category pages and book detail pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "crawler_etl" / "config" / "fahasa_config.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw" / "fahasa_books.json"


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def compact_text(value: str | None) -> str | None:
    return " ".join(value.split()) if value else None


def fold_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    folded = "".join(character for character in normalized if not unicodedata.combining(character))
    return folded.replace("đ", "d").replace("Đ", "D").lower()


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"-?\d[\d.,]*", str(value))
    if not match:
        return None
    text = match.group(0)
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", "").replace(".", "")
    try:
        return float(text)
    except ValueError:
        return None


def json_ld_product(soup: BeautifulSoup) -> dict[str, Any]:
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.get_text(strip=True))
        except json.JSONDecodeError:
            continue
        records = payload if isinstance(payload, list) else [payload]
        for record in records:
            if isinstance(record, dict) and record.get("@type") == "Product":
                return record
    return {}


def metadata_rows(soup: BeautifulSoup) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for row in soup.select("tr, .product-view-sa-supplier, .product-view-sa-author"):
        cells = [compact_text(cell.get_text(" ", strip=True)) for cell in row.select("th, td, span")]
        values = [cell for cell in cells if cell]
        if len(values) >= 2:
            metadata[fold_text(values[0]).rstrip(":")] = values[-1]
    return metadata


def find_metadata(metadata: dict[str, str], *labels: str) -> str | None:
    for key, value in metadata.items():
        if any(label in key for label in labels):
            return value
    return None


def detail_book(
    session: requests.Session,
    url: str,
    category: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    product = json_ld_product(soup)
    metadata = metadata_rows(soup)
    offers = product.get("offers") or {}
    aggregate_rating = product.get("aggregateRating") or {}
    sku = product.get("sku") or find_metadata(metadata, "ma hang", "sku")
    fallback_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    original_price_node = soup.select_one(".old-price .price, .price-box .old-price")
    discount_node = soup.select_one(".discount-percent, .discount")
    return {
        "book_id": sku or fallback_id,
        "source": "fahasa",
        "title": product.get("name") or compact_text(soup.title.string if soup.title else None),
        "author": find_metadata(metadata, "tac gia", "author"),
        "publisher": find_metadata(metadata, "nha xuat ban", "publisher"),
        "language_group": category.get("language_group"),
        "main_category": category.get("name"),
        "sub_category": find_metadata(metadata, "nhom san pham", "category") or category.get("name"),
        "price": offers.get("price") if isinstance(offers, dict) else None,
        "original_price": parse_number(original_price_node.get_text(" ", strip=True)) if original_price_node else None,
        "discount_rate": parse_number(discount_node.get_text(" ", strip=True)) if discount_node else None,
        "rating": aggregate_rating.get("ratingValue") if isinstance(aggregate_rating, dict) else None,
        "review_count": aggregate_rating.get("reviewCount") if isinstance(aggregate_rating, dict) else None,
        "sold_count": 0,
        "publish_year": find_metadata(metadata, "nam xuat ban", "publish year"),
        "page_count": find_metadata(metadata, "so trang", "number of pages"),
        "url": url,
    }


def product_links(
    session: requests.Session,
    category: dict[str, Any],
    config: dict[str, Any],
) -> list[str]:
    links: list[str] = []
    for page in range(1, int(config["max_pages_per_category"]) + 1):
        response = session.get(
            category["url"],
            params={"p": page},
            timeout=config["timeout_seconds"],
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        for selector in config["selectors"]["product_links"]:
            for node in soup.select(selector):
                href = node.get("href")
                if href:
                    links.append(urljoin(category["url"], href))
        time.sleep(float(config["request_delay_seconds"]))
    unique_links = list(dict.fromkeys(links))
    return unique_links[: int(config["max_products_per_category"])]


def crawl(config: dict[str, Any]) -> list[dict[str, Any]]:
    session = requests.Session()
    session.headers.update({"User-Agent": "BookBigDataSystem/1.0"})
    books: list[dict[str, Any]] = []
    for category in config["categories"]:
        for url in product_links(session, category, config):
            try:
                books.append(detail_book(session, url, category, int(config["timeout_seconds"])))
            except requests.RequestException as error:
                print(f"Skip {url}: {error}")
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
    print(f"Wrote {len(books)} Fahasa books to {args.output}")


if __name__ == "__main__":
    main()
