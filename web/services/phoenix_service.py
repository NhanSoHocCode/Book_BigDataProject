from __future__ import annotations

import glob
import os
import re
from contextlib import closing
from decimal import Decimal
from pathlib import Path
from typing import Any

from attrs import field
import jpype


VIEW_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")
SAFE_QUERY_PATTERN = re.compile(r"^\s*(SELECT|EXPLAIN)\b", re.IGNORECASE)

TEXT_COLUMNS = {
    "source": '"info"."source"',
    "title": '"info"."title"',
    "author": '"info"."author"',
    "publisher": '"info"."publisher"',
    "language_group": '"info"."language_group"',
    "main_category": '"info"."main_category"',
    "sub_category": '"info"."sub_category"',
    "publish_year": '"info"."publish_year"',
    "page_count": '"info"."page_count"',
    "url": '"info"."url"',
    "price": '"price"."price"',
    "original_price": '"price"."original_price"',
    "discount_rate": '"price"."discount_rate"',
    "rating": '"stat"."rating"',
    "review_count": '"stat"."review_count"',
    "sold_count": '"stat"."sold_count"',
}

NUMERIC_TYPES = {
    "price": "DOUBLE",
    "original_price": "DOUBLE",
    "discount_rate": "DOUBLE",
    "rating": "DOUBLE",
    "review_count": "BIGINT",
    "sold_count": "BIGINT",
    "publish_year": "INTEGER",
    "page_count": "INTEGER",
}

BOOK_FIELDS = [
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


def serialize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if hasattr(value, "isoformat"):
        return value.isoformat(sep=" ")
    return value


class PhoenixBookService:
    def __init__(self) -> None:
        self.jdbc_url = os.getenv(
            "PHOENIX_JDBC_URL",
            "jdbc:phoenix:localhost:2181",
        ).strip()
        self.jdbc_driver = os.getenv(
            "PHOENIX_JDBC_DRIVER",
            "org.apache.phoenix.jdbc.PhoenixDriver",
        ).strip()
        self.jdbc_classpath = os.getenv(
            "PHOENIX_JDBC_CLASSPATH",
            os.pathsep.join([
                "$HOME/phoenix/phoenix-client-lite-hbase-2.6-5.3.0.jar",
                "$HBASE_HOME/conf",
                "$HADOOP_HOME/etc/hadoop",
            ]),
        )
        print(repr(os.getenv("PHOENIX_BOOKS_VIEW")))
        self.view = os.getenv("PHOENIX_BOOKS_VIEW", "bookbigdata.books_hbase").strip()
        # if not VIEW_PATTERN.fullmatch(self.view):
        #     raise ValueError("PHOENIX_BOOKS_VIEW không phải tên view hợp lệ.")
        self.query_limit = max(1, int(os.getenv("PHOENIX_QUERY_MAX_ROWS", "200")))

    def classpath_entries(self) -> list[str]:
        entries: list[str] = []
        for raw_entry in self.jdbc_classpath.split(os.pathsep):
            raw_entry = raw_entry.strip()
            if not raw_entry:
                continue
            expanded = os.path.expandvars(os.path.expanduser(raw_entry))
            matches = glob.glob(expanded) if glob.has_magic(expanded) else [expanded]
            entries.extend(matches)

        missing = [entry for entry in entries if not Path(entry).exists()]
        if missing:
            raise RuntimeError(
                "Không tìm thấy Phoenix JDBC classpath: " + ", ".join(missing)
            )
        return entries

    def connection(self):
        try:
            import jaydebeapi
        except ImportError as error:
            raise RuntimeError(
                "Thiếu thư viện JayDeBeApi/JPype1. "
                "Hãy chạy pip install -r requirements.txt trong WSL."
            ) from error
        if jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()
        connection = jaydebeapi.connect(
            self.jdbc_driver,
            self.jdbc_url,
            [],
            self.classpath_entries(),
        )
        try:
            connection.jconn.setAutoCommit(True)
        except AttributeError:
            pass
        return connection

    @staticmethod
    def _row(cursor, values: tuple[Any, ...]) -> dict[str, Any]:
        return {
            str(description[0]).casefold(): serialize(value)
            for description, value in zip(cursor.description or [], values)
        }

    def fetch_all(
        self,
        query: str,
        params: tuple[Any, ...] = (),
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        with closing(self.connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute(query, params)
                values = cursor.fetchmany(limit) if limit else cursor.fetchall()
                return [self._row(cursor, row) for row in values]

    @staticmethod
    def row_key(source: str, book_id: str) -> str:
        source = str(source).strip()
        book_id = str(book_id).strip()
        
        if book_id.startswith(f"{source}_"):
            book_id = book_id[len(source) + 1:] 
            
        return f"{source}#{book_id}"

    @staticmethod
    def _number_expression(field: str) -> str:
        #return f"CAST(TO_NUMBER({TEXT_COLUMNS[field]}) AS {NUMERIC_TYPES[field]})"
        col = TEXT_COLUMNS[field]
        typ = NUMERIC_TYPES[field]
        return (
            f"CASE WHEN REGEXP_LIKE({col}, '^[0-9]+(\\.[0-9]+)?$') "
            f"THEN CAST(TO_NUMBER({col}) AS {typ}) ELSE 0 END"
        )

    def _select_expression(self) -> str:
        selected = ["ROWKEY AS row_key"]
        for field in BOOK_FIELDS:
            # Lấy thẳng giá trị VARCHAR gốc từ HBase, không CAST ở đây nữa để tránh crash do dữ liệu bẩn
            selected.append(f"{TEXT_COLUMNS[field]} AS {field}")
        return ", ".join(selected)

    @staticmethod
    def _with_book_id(row: dict[str, Any]) -> dict[str, Any]:
        if not row:
            return {}

        row_key = str(row.get("ROWKEY") or row.get("rowkey") or row.get("row_key") or "")

        source = str(row.get("source") or row.get("SOURCE") or "")
        book_id = str(row.get("book_id") or row.get("BOOK_ID") or "")
        
        if "#" in row_key:
            parts = row_key.split("#", 1)
            if not source:
                source = parts[0]
            if not book_id:
                book_id = parts[1]

        row["row_key"] = row_key
        row["source"] = source
        row["book_id"] = book_id

        for field, target_type in NUMERIC_TYPES.items():
            actual_field = field if field in row else field.upper()
            
            if actual_field in row and row[actual_field] is not None:
                val_str = str(row[actual_field]).strip()
                try:
                    if target_type == "DOUBLE":
                        row[field] = float(val_str)
                    else:
                        row[field] = int(float(val_str))
                except (ValueError, TypeError):
                    row[field] = 0  
                    
        return row

    def list_books(
        self,
        filters: dict[str, str],
        page: int = 1,
        page_size: int = 15,
    ) -> tuple[list[dict[str, Any]], int]:
        clauses: list[str] = []
        params: list[Any] = []

        query_text = filters.get("q", "").strip()
        if query_text:
            clauses.append(
                f"(UPPER({TEXT_COLUMNS['title']}) LIKE ? OR UPPER(ROWKEY) LIKE ?)"
            )
            value = f"%{query_text.upper()}%"
            params.extend([value, value])

        for filter_name, column in (
            ("source", TEXT_COLUMNS["source"]),
            ("category", TEXT_COLUMNS["main_category"]),
            ("sub_category", TEXT_COLUMNS["sub_category"]),
        ):
            value = filters.get(filter_name, "").strip()
            if value:
                clauses.append(f"{column} = ?")
                params.append(value)

        for filter_name, column in (
            ("author", TEXT_COLUMNS["author"]),
            ("publisher", TEXT_COLUMNS["publisher"]),
        ):
            value = filters.get(filter_name, "").strip()
            if value:
                clauses.append(f"UPPER({column}) LIKE ?")
                params.append(f"%{value.upper()}%")

        for filter_name, operator in (("min_price", ">="), ("max_price", "<=")):
            value = filters.get(filter_name, "").strip()
            if value:
                clauses.append(f"{self._number_expression('price')} {operator} ?")
                params.append(float(value))

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        count_rows = self.fetch_all(
            f"SELECT COUNT(*) AS total FROM {self.view}{where}",
            tuple(params),
        )
        total = int(list(count_rows[0].values())[0]) if count_rows else 0
        offset = max(0, page - 1) * page_size
        rows = self.fetch_all(
            f"SELECT ROWKEY, {self._select_expression()} FROM {self.view}{where} "
            f"ORDER BY {TEXT_COLUMNS['title']} LIMIT {int(page_size)} OFFSET {int(offset)}",
            tuple(params),
        )
        return [self._with_book_id(row) for row in rows], total

    def get_book(self, source: str, book_id: str) -> dict[str, Any] | None:
        rows = self.fetch_all(
            f"SELECT {self._select_expression()} FROM {self.view} WHERE ROWKEY = ?",
            (self.row_key(source, book_id),),
        )
        if rows:
            row = rows[0]
            if "rowkey" in row and "row_key" not in row:
                row["row_key"] = row["rowkey"]
        return self._with_book_id(rows[0]) if rows else None
        
    def book_category_tree(self) -> dict[str, list[str]]:
        rows = self.fetch_all(
            f"SELECT DISTINCT {TEXT_COLUMNS['main_category']} AS main_category, "
            f"{TEXT_COLUMNS['sub_category']} AS sub_category FROM {self.view} "
            f"WHERE {TEXT_COLUMNS['main_category']} IS NOT NULL "
            f"ORDER BY {TEXT_COLUMNS['main_category']}, {TEXT_COLUMNS['sub_category']}"
        )
        tree: dict[str, set[str]] = {}
        for row in rows:
            main_category = str(row.get("main_category") or "").strip()
            sub_category = str(row.get("sub_category") or "").strip()
            if not main_category:
                continue
            tree.setdefault(main_category, set())
            if sub_category:
                tree[main_category].add(sub_category)
        return {
            category: sorted(subcategories, key=str.casefold)
            for category, subcategories in tree.items()
        }

    def book_categories(self) -> list[str]:
        return list(self.book_category_tree())

    def dashboard_metrics(self) -> dict[str, int]:
        metrics = {
            "total_books": 0,
            "categories": 0,
            "authors": 0,
            "tiki_books": 0,
            "fahasa_books": 0
        }
        
        try:           
            # tổng số sách
            total_rows = self.fetch_all(f'SELECT COUNT(*) FROM {self.view}')
            if total_rows:
                metrics["total_books"] = int(list(total_rows[0].values())[0])

            # tổng category
            cat_rows = self.fetch_all(f'SELECT COUNT(DISTINCT {TEXT_COLUMNS["main_category"]}) FROM {self.view}')
            if cat_rows:
                metrics["categories"] = int(list(cat_rows[0].values())[0])

            # tổng tác giả
            auth_rows = self.fetch_all(f'SELECT COUNT(DISTINCT {TEXT_COLUMNS["author"]}) FROM {self.view}')
            if auth_rows:
                metrics["authors"] = int(list(auth_rows[0].values())[0])

            # số sách Tiki
            tiki_rows = self.fetch_all(f"SELECT COUNT(*) FROM {self.view} WHERE ROWKEY LIKE 'tiki#%'")
            if tiki_rows:
                metrics["tiki_books"] = int(list(tiki_rows[0].values())[0])

            # số sách Fahasa
            fahasa_rows = self.fetch_all(f"SELECT COUNT(*) FROM {self.view} WHERE ROWKEY LIKE 'fahasa#%'")
            if fahasa_rows:
                metrics["fahasa_books"] = int(list(fahasa_rows[0].values())[0])

        except Exception as e:
            print(f"Lỗi: {e}\n")

        return metrics

    def healthcheck(self) -> tuple[bool, str]:
        try:
            self.fetch_all(f"SELECT ROWKEY FROM {self.view} LIMIT 1")
            return True, "Đã kết nối"
        except Exception as error:
            return False, str(error)

    def phoenix_query(self, sql: str) -> tuple[list[dict[str, Any]], str | None]:
        statement = sql.strip()
        if not statement:
            return [], None
        if ";" in statement.rstrip(";"):
            return [], "Chỉ được chạy một câu lệnh mỗi lần."
        statement = statement.rstrip(";").strip()
        if not SAFE_QUERY_PATTERN.match(statement):
            return [], "Trang SQL chỉ cho phép SELECT hoặc EXPLAIN."
        try:
            rows = self.fetch_all(statement, limit=self.query_limit + 1)
        except Exception as error:
            return [], f"Phoenix JDBC trả lỗi: {error}"
        processed_rows = []
        for row in rows:
            if "rowkey" in row and "row_key" not in row:
                row["row_key"] = row["rowkey"]
            
            if "row_key" in row and "#" in str(row["row_key"]):
                row = self._with_book_id(row)

            uppercased_row = {k.upper(): v for k, v in row.items()}
            processed_rows.append(uppercased_row)
        if len(processed_rows) > self.query_limit:
            return processed_rows[:self.query_limit], (
                f"Kết quả được giới hạn ở {self.query_limit} dòng để bảo vệ Web."
            )

        if len(rows) > self.query_limit:
            return rows[:self.query_limit], (
                f"Kết quả được giới hạn ở {self.query_limit} dòng để bảo vệ Web."
            )
        return processed_rows, None