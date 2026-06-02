"""Normalize raw book records from Tiki and Fahasa into one schema."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FIELDS = [
    "book_id",
    "source",
    "title",
    "author",
    "publisher",
    "language_group",
    "main_category",
    "sub_category",
    "price",
    "original_price",
    "discount_rate",
    "rating",
    "review_count",
    "sold_count",
    "publish_year",
    "page_count",
    "url",
]


def clean_text(value: Any, default: str | None = None) -> str | None:
    if value is None:
        return default
    text = " ".join(str(value).replace("\x00", "").split())
    return text or default


def number(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d[\d.,]*", str(value))
    if not match:
        return default
    text = match.group(0)
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif text.count(".") > 1 or text.count(",") > 1:
        text = text.replace(".", "").replace(",", "")
    elif "," in text:
        text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return default


def integer(value: Any, default: int | None = None) -> int | None:
    parsed = number(value)
    return int(parsed) if parsed is not None else default


def tiki_url(value: Any) -> str | None:
    url = clean_text(value)
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"https://tiki.vn/{url.lstrip('/')}"


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    source = clean_text(record.get("source"), "unknown").lower()
    raw_price = number(record.get("price"), 0.0)
    original_price = number(record.get("original_price"), raw_price)
    discount_rate = number(record.get("discount_rate"))
    if discount_rate is None and original_price and raw_price is not None:
        discount_rate = max(0.0, round((original_price - raw_price) * 100 / original_price, 2))
    normalized = {
        "book_id": clean_text(record.get("book_id")),
        "source": source,
        "title": clean_text(record.get("title")),
        "author": clean_text(record.get("author"), "Unknown"),
        "publisher": clean_text(record.get("publisher"), "Unknown"),
        "language_group": clean_text(record.get("language_group"), "Unknown"),
        "main_category": clean_text(record.get("main_category"), "Unknown"),
        "sub_category": clean_text(record.get("sub_category"), "Unknown"),
        "price": raw_price,
        "original_price": original_price,
        "discount_rate": discount_rate or 0.0,
        "rating": number(record.get("rating"), 0.0),
        "review_count": integer(record.get("review_count"), 0),
        "sold_count": integer(record.get("sold_count"), 0),
        "publish_year": integer(record.get("publish_year")),
        "page_count": integer(record.get("page_count")),
        "url": tiki_url(record.get("url")) if source == "tiki" else clean_text(record.get("url")),
    }
    return {field: normalized[field] for field in FIELDS}


def normalize_file(input_path: Path, output_path: Path) -> list[dict[str, Any]]:
    with input_path.open("r", encoding="utf-8") as file:
        records = json.load(file)
    normalized = [normalize_record(record) for record in records]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, ensure_ascii=False, indent=2)
    return normalized


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = normalize_file(args.input, args.output)
    print(f"Wrote {len(records)} normalized records to {args.output}")


if __name__ == "__main__":
    main()
