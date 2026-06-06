"""Import ETL output from books_clean.csv into MySQL."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from typing import Any, Iterator

import mysql.connector
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = PROJECT_ROOT / "data" / "clean" / "books_clean.csv"
FIELDS = [
    "book_id", "source", "title", "author", "publisher", "language_group",
    "main_category", "sub_category", "price", "original_price", "discount_rate",
    "rating", "review_count", "sold_count", "publish_year", "page_count", "url",
]


def connection_config() -> dict[str, Any]:
    load_dotenv(PROJECT_ROOT / ".env")
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "database": os.getenv("MYSQL_DATABASE", "book_big_data"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
    }


def empty_to_none(value: str) -> str | None:
    return value if value != "" else None


def csv_rows(path: Path) -> Iterator[tuple[Any, ...]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            yield tuple(empty_to_none(row.get(field, "")) for field in FIELDS)


def import_books(path: Path) -> int:
    placeholders = ", ".join(["%s"] * len(FIELDS))
    updates = ", ".join(f"{field}=VALUES({field})" for field in FIELDS[2:])
    query = (
        f"INSERT INTO books ({', '.join(FIELDS)}) VALUES ({placeholders}) "
        f"ON DUPLICATE KEY UPDATE {updates}"
    )
    connection = mysql.connector.connect(**connection_config())
    try:
        cursor = connection.cursor()
        rows = list(csv_rows(path))
        cursor.executemany(query, rows)
        connection.commit()
        return len(rows)
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    count = import_books(args.csv)
    print(f"Imported {count} books from {args.csv}")


if __name__ == "__main__":
    main()
