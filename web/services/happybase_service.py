from __future__ import annotations

import os
from typing import Any


COLUMN_MAP = {
    "source": b"info:source",
    "title": b"info:title",
    "author": b"info:author",
    "publisher": b"info:publisher",
    "language_group": b"info:language_group",
    "main_category": b"info:main_category",
    "sub_category": b"info:sub_category",
    "publish_year": b"info:publish_year",
    "page_count": b"info:page_count",
    "url": b"info:url",
    "price": b"price:price",
    "original_price": b"price:original_price",
    "discount_rate": b"price:discount_rate",
    "rating": b"stat:rating",
    "review_count": b"stat:review_count",
    "sold_count": b"stat:sold_count",
}


class HappyBaseBookService:

    def __init__(self) -> None:
        self.table_name = os.getenv(
            "HBASE_TABLE",
            "bookbigdata:books_hbase",
        ).strip()
        self.pool_size = max(1, int(os.getenv("HBASE_THRIFT_POOL_SIZE", "5")))
        self.host = os.getenv("HBASE_THRIFT_HOST", "localhost")
        self.port = int(os.getenv("HBASE_THRIFT_PORT", "9090"))
        self.timeout = int(os.getenv("HBASE_THRIFT_TIMEOUT_MS", "10000"))
        self.compat = os.getenv("HBASE_THRIFT_COMPAT", "0.98")
        self.transport = os.getenv("HBASE_THRIFT_TRANSPORT", "buffered")
        self.protocol = os.getenv("HBASE_THRIFT_PROTOCOL", "binary")
        self._connection_pool = None

    @property
    def pool(self):
        if self._connection_pool is None:
            try:
                import happybase
            except ImportError as error:
                raise RuntimeError(
                    "Thiếu thư viện happybase. Hãy chạy pip install -r requirements.txt."
                ) from error
            self._connection_pool = happybase.ConnectionPool(
                size=self.pool_size,
                host=self.host,
                port=self.port,
                timeout=self.timeout,
                compat=self.compat,
                transport=self.transport,
                protocol=self.protocol,
            )
        return self._connection_pool

    @staticmethod
    def row_key(source: str, book_id: str) -> bytes:
        source = str(source).strip()
        book_id = str(book_id).strip()

        if book_id.startswith(f"{source}_"):
            book_id = book_id[len(source) + 1:]
            
        return f"{source}#{book_id}".encode("utf-8")

    @staticmethod
    def encode(value: Any) -> bytes:
        return str(value).encode("utf-8")

    def save_book(self, data: dict[str, Any]) -> None:
        row_key = self.row_key(str(data["source"]), str(data["book_id"]))
        values: dict[bytes, bytes] = {}
        empty_columns: list[bytes] = []
        for field, column in COLUMN_MAP.items():
            value = data.get(field)
            if value in ("", None):
                empty_columns.append(column)
            else:
                values[column] = self.encode(value)

        with self.pool.connection() as connection:
            table = connection.table(self.table_name)
            if values:
                table.put(row_key, values)
            if empty_columns:
                table.delete(row_key, columns=empty_columns)

    def exists(self, source: str, book_id: str) -> bool:
        with self.pool.connection() as connection:
            row = connection.table(self.table_name).row(
                self.row_key(source, book_id),
                columns=[b"info:source"],
            )
        return bool(row)

    def delete_book(self, source: str, book_id: str) -> None:
        with self.pool.connection() as connection:
            connection.table(self.table_name).delete(self.row_key(source, book_id))

    def healthcheck(self) -> tuple[bool, str]:
        try:
            with self.pool.connection() as connection:
                tables = {
                    name.decode("utf-8", errors="replace")
                    if isinstance(name, bytes)
                    else str(name)
                    for name in connection.tables()
                }
            if self.table_name not in tables:
                return False, f"Không tìm thấy bảng {self.table_name}"
            return True, "Đã kết nối"
        except Exception as error:
            return False, str(error)
