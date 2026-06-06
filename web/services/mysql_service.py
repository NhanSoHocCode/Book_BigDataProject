"""Small MySQL data-access layer for the Flask application."""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

import mysql.connector
from mysql.connector import pooling


BOOK_FIELDS = [
    "book_id", "source", "title", "author", "publisher", "language_group",
    "main_category", "sub_category", "price", "original_price", "discount_rate",
    "rating", "review_count", "sold_count", "publish_year", "page_count", "url",
]


def serialize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat(sep=" ")
    return value


def serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: serialize(value) for key, value in row.items()}


class MySQLService:
    def __init__(self) -> None:
        self.pool = pooling.MySQLConnectionPool(
            pool_name="book_big_data_pool",
            pool_size=5,
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            database=os.getenv("MYSQL_DATABASE", "book_big_data"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
        )

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            return [serialize_row(row) for row in cursor.fetchall()]
        finally:
            connection.close()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        connection = self.pool.get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount
        finally:
            connection.close()

    def list_books(self, filters: dict[str, str], page: int = 1, page_size: int = 30) -> tuple[list[dict[str, Any]], int]:
        clauses: list[str] = []
        params: list[Any] = []
        like_fields = {
            "q": ("title",),
            "author": ("author",),
            "publisher": ("publisher",),
            "category": ("main_category",),
        }
        for name, fields in like_fields.items():
            value = filters.get(name, "").strip()
            if value:
                expression = " OR ".join(f"{field} LIKE %s" for field in fields)
                clauses.append(f"({expression})")
                params.extend([f"%{value}%"] * len(fields))
        source = filters.get("source", "").strip()
        if source:
            clauses.append("source = %s")
            params.append(source)
        for name, operator in (("min_price", ">="), ("max_price", "<=")):
            value = filters.get(name, "").strip()
            if value:
                clauses.append(f"price {operator} %s")
                params.append(value)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        count = self.fetch_all(f"SELECT COUNT(*) AS total FROM books{where}", tuple(params))[0]["total"]
        offset = max(0, page - 1) * page_size
        rows = self.fetch_all(
            f"SELECT {', '.join(BOOK_FIELDS)} FROM books{where} "
            "ORDER BY updated_at DESC LIMIT %s OFFSET %s",
            tuple(params + [page_size, offset]),
        )
        return rows, int(count)

    def get_book(self, source: str, book_id: str) -> dict[str, Any] | None:
        rows = self.fetch_all(
            f"SELECT {', '.join(BOOK_FIELDS)} FROM books WHERE source = %s AND book_id = %s",
            (source, book_id),
        )
        return rows[0] if rows else None

    def save_book(self, data: dict[str, Any]) -> None:
        defaults = {
            "author": "Unknown",
            "publisher": "Unknown",
            "language_group": "Unknown",
            "main_category": "Unknown",
            "sub_category": "Unknown",
            "price": 0,
            "original_price": 0,
            "discount_rate": 0,
            "rating": 0,
            "review_count": 0,
            "sold_count": 0,
        }
        values = tuple(
            data.get(field) if data.get(field) not in ("", None) else defaults.get(field)
            for field in BOOK_FIELDS
        )
        placeholders = ", ".join(["%s"] * len(BOOK_FIELDS))
        updates = ", ".join(f"{field}=VALUES({field})" for field in BOOK_FIELDS[2:])
        self.execute(
            f"INSERT INTO books ({', '.join(BOOK_FIELDS)}) VALUES ({placeholders}) "
            f"ON DUPLICATE KEY UPDATE {updates}",
            values,
        )

    def delete_book(self, source: str, book_id: str) -> None:
        self.execute("DELETE FROM books WHERE source = %s AND book_id = %s", (source, book_id))

    def log_backup(
        self,
        storage_type: str,
        action_type: str,
        scope_name: str,
        backup_path: str,
        status: str,
        message: str = "",
    ) -> None:
        self.execute(
            "INSERT INTO backup_logs "
            "(storage_type, action_type, scope_name, backup_path, status, message) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (storage_type, action_type, scope_name, backup_path, status, message),
        )

    def list_backup_logs(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.fetch_all(
            "SELECT id, storage_type, action_type, scope_name, backup_path, status, message, created_at "
            "FROM backup_logs ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
