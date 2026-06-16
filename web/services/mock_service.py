"""Dữ liệu mẫu cho giai đoạn dựng giao diện Flask.

Khi HBase, Phoenix, WebHDFS và HBase Snapshot đã sẵn sàng, thay các hàm trong
service này bằng service thật tương ứng:

- Phoenix cho danh sách, tìm kiếm và truy vấn SQL.
- HappyBase cho thêm, cập nhật và xóa sách trực tiếp trên HBase.
- WebHDFS cho Analytics và Data Quality.
- Script HBase Snapshot cho Backup/Restore.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any


class MockDataService:
    """Service giả lập để web chạy được trước khi có backend Big Data thật."""

    def __init__(self) -> None:
        self.books = [
            {
                "book_id": "279342306",
                "source": "tiki",
                "row_key": "tiki#279342306",
                "title": "The Saigon Times Weekly kỳ 18-2026",
                "author": "TẠP CHÍ KINH TẾ SÀI GÒN",
                "publisher": "Unknown",
                "language_group": "English",
                "main_category": "Magazines",
                "sub_category": "Weekly Magazine",
                "price": 19000,
                "original_price": 19000,
                "discount_rate": 0,
                "rating": 0,
                "review_count": 0,
                "sold_count": 3,
                "publish_year": None,
                "page_count": None,
                "url": "https://tiki.vn/the-saigon-times-weekly-ky-18-2026-p279342306.html",
            },
            {
                "book_id": "tiki-atomic-habits",
                "source": "tiki",
                "row_key": "tiki#tiki-atomic-habits",
                "title": "Atomic Habits",
                "author": "James Clear",
                "publisher": "Penguin Random House",
                "language_group": "English",
                "main_category": "Personal Development",
                "sub_category": "Self Help",
                "price": 228000,
                "original_price": 260000,
                "discount_rate": 12,
                "rating": 4.8,
                "review_count": 840,
                "sold_count": 12500,
                "publish_year": 2018,
                "page_count": 320,
                "url": "https://tiki.vn/",
            },
            {
                "book_id": "fahasa-nha-gia-kim",
                "source": "fahasa",
                "row_key": "fahasa#fahasa-nha-gia-kim",
                "title": "Nhà Giả Kim",
                "author": "Paulo Coelho",
                "publisher": "NXB Văn Học",
                "language_group": "Vietnamese",
                "main_category": "Văn học",
                "sub_category": "Tiểu thuyết",
                "price": 79000,
                "original_price": 99000,
                "discount_rate": 20,
                "rating": 4.7,
                "review_count": 1250,
                "sold_count": 24200,
                "publish_year": 2020,
                "page_count": 228,
                "url": "https://www.fahasa.com/",
            },
            {
                "book_id": "fahasa-dac-nhan-tam",
                "source": "fahasa",
                "row_key": "fahasa#fahasa-dac-nhan-tam",
                "title": "Đắc Nhân Tâm",
                "author": "Dale Carnegie",
                "publisher": "NXB Tổng Hợp TP.HCM",
                "language_group": "Vietnamese",
                "main_category": "Tâm lý - Kỹ năng sống",
                "sub_category": "Kỹ năng sống",
                "price": 86000,
                "original_price": 108000,
                "discount_rate": 20,
                "rating": 4.6,
                "review_count": 980,
                "sold_count": 19800,
                "publish_year": 2021,
                "page_count": 320,
                "url": "https://www.fahasa.com/",
            },
            {
                "book_id": "tiki-one-piece",
                "source": "tiki",
                "row_key": "tiki#tiki-one-piece",
                "title": "One Piece - Tập 100",
                "author": "Eiichiro Oda",
                "publisher": "NXB Kim Đồng",
                "language_group": "Vietnamese",
                "main_category": "Truyện Tranh, Manga, Comic",
                "sub_category": "Manga",
                "price": 25000,
                "original_price": 25000,
                "discount_rate": 0,
                "rating": 4.9,
                "review_count": 420,
                "sold_count": 7600,
                "publish_year": 2022,
                "page_count": 192,
                "url": "https://tiki.vn/",
            },
        ]
        # Bổ sung đủ dữ liệu mẫu để kiểm tra bảng 15 dòng và phân trang.
        # Khi kết nối Phoenix thật, danh sách này được thay bằng kết quả SELECT.
        self.books.extend(self._generated_books())
        self.snapshots = [
            {
                "name": "books_hbase_20260608_103000",
                "created_at": "2026-06-08 10:30",
                "table_name": "books_hbase",
                "status": "OK",
                "note": "Mock snapshot gần nhất",
            },
            {
                "name": "books_hbase_20260607_220000",
                "created_at": "2026-06-07 22:00",
                "table_name": "books_hbase",
                "status": "OK",
                "note": "Mock snapshot trước đó",
            },
        ]

    def dashboard(self) -> dict[str, Any]:
        total_books = len(self.books)
        tiki_books = sum(1 for book in self.books if book["source"] == "tiki")
        fahasa_books = sum(1 for book in self.books if book["source"] == "fahasa")
        categories = {book["main_category"] for book in self.books}
        authors = {book["author"] for book in self.books}
        last_backup = self.snapshots[0]["created_at"] if self.snapshots else "Chưa có"
        return {
            "total_books": total_books,
            "tiki_books": tiki_books,
            "fahasa_books": fahasa_books,
            "categories": len(categories),
            "authors": len(authors),
            "last_backup": last_backup,
            "statuses": [
                {"name": "Phoenix JDBC", "status": "Mock Connected", "variant": "success"},
                {"name": "HBase Thrift / HappyBase", "status": "Mock Connected", "variant": "success"},
                {"name": "WebHDFS", "status": "Mock Connected", "variant": "success"},
                {"name": "Analytics output", "status": "Dữ liệu mẫu", "variant": "warning"},
                {"name": "Data Quality report", "status": "Dữ liệu mẫu", "variant": "warning"},
            ],
        }

    def list_books(
        self,
        filters: dict[str, str],
        page: int = 1,
        page_size: int = 15,
    ) -> tuple[list[dict[str, Any]], int]:
        rows = deepcopy(self.books)
        q = filters.get("q", "").casefold().strip()
        if q:
            rows = [
                book for book in rows
                if q in book["title"].casefold() or q in book["book_id"].casefold()
            ]
        for key, field, exact_match in (
            ("source", "source", True),
            ("category", "main_category", True),
            ("sub_category", "sub_category", True),
            ("author", "author", False),
            ("publisher", "publisher", False),
        ):
            value = filters.get(key, "").casefold().strip()
            if value:
                if exact_match:
                    rows = [
                        book for book in rows
                        if value == str(book.get(field, "")).casefold().strip()
                    ]
                else:
                    rows = [
                        book for book in rows
                        if value in str(book.get(field, "")).casefold()
                    ]
        min_price = self._number(filters.get("min_price"))
        max_price = self._number(filters.get("max_price"))
        if min_price is not None:
            rows = [book for book in rows if float(book.get("price") or 0) >= min_price]
        if max_price is not None:
            rows = [book for book in rows if float(book.get("price") or 0) <= max_price]
        total = len(rows)
        start = (max(1, page) - 1) * page_size
        return rows[start:start + page_size], total

    def book_categories(self) -> list[str]:
        """Danh sách category dùng cho combobox lọc.

        Khi tích hợp Phoenix thật, thay bằng truy vấn SELECT DISTINCT
        MAIN_CATEGORY FROM BOOKS để combobox luôn khớp dữ liệu trong HBase.
        """
        return sorted({
            str(book.get("main_category", "")).strip()
            for book in self.books
            if str(book.get("main_category", "")).strip()
        }, key=str.casefold)

    def book_category_tree(self) -> dict[str, list[str]]:
        """Cây category hai tầng dùng cho combobox phụ thuộc trên Web.

        Khi tích hợp HBase thật, PhoenixBookService nên thay hàm này bằng:
        SELECT DISTINCT MAIN_CATEGORY, SUB_CATEGORY FROM BOOKS
        rồi gom kết quả theo MAIN_CATEGORY trước khi trả cho Flask.
        """
        tree: dict[str, set[str]] = {}
        for book in self.books:
            main_category = str(book.get("main_category", "")).strip()
            sub_category = str(book.get("sub_category", "")).strip()
            if not main_category:
                continue
            tree.setdefault(main_category, set())
            if sub_category:
                tree[main_category].add(sub_category)
        return {
            main_category: sorted(sub_categories, key=str.casefold)
            for main_category, sub_categories in sorted(
                tree.items(),
                key=lambda item: item[0].casefold(),
            )
        }

    def get_book(self, source: str, book_id: str) -> dict[str, Any] | None:
        for book in self.books:
            if book["source"] == source and book["book_id"] == book_id:
                return deepcopy(book)
        return None

    def exists(self, source: str, book_id: str) -> bool:
        """Giả lập kiểm tra RowKey của HappyBase trước khi CRUD."""
        return self.get_book(source, book_id) is not None

    def save_book(self, data: dict[str, Any]) -> None:
        """Giả lập HappyBase ``put`` trực tiếp vào HBase."""
        data = deepcopy(data)
        data["row_key"] = f"{data['source']}#{data['book_id']}"
        for numeric in (
            "price", "original_price", "discount_rate", "rating",
            "review_count", "sold_count", "publish_year", "page_count",
        ):
            data[numeric] = self._number(data.get(numeric), default=data.get(numeric))
        for index, book in enumerate(self.books):
            if book["source"] == data["source"] and book["book_id"] == data["book_id"]:
                self.books[index] = {**book, **data}
                return
        self.books.insert(0, data)

    def delete_book(self, source: str, book_id: str) -> None:
        """Giả lập HappyBase ``delete`` trực tiếp trên HBase."""
        self.books = [
            book for book in self.books
            if not (book["source"] == source and book["book_id"] == book_id)
        ]

    def phoenix_query(self, sql: str) -> tuple[list[dict[str, Any]], str | None]:
        """Giả lập trang nhập SELECT.

        Khi có Phoenix JDBC thật, thay hàm này bằng client gửi SQL tới Phoenix
        và chỉ cho phép SELECT/EXPLAIN để tránh thao tác nguy hiểm.
        """
        normalized = sql.strip().casefold()
        if not normalized:
            return [], None
        if not (normalized.startswith("select") or normalized.startswith("explain")):
            return [], "Mock hiện chỉ cho phép SELECT hoặc EXPLAIN."
        if normalized.startswith("explain"):
            return [{"plan": "CLIENT PARALLEL 1-WAY FULL SCAN OVER BOOKS (mock)"}], None
        return deepcopy(self.books[:20]), None

    def analytics_datasets(self) -> dict[str, tuple[str, str]]:
        return {
            "source_count": ("Số sách theo nguồn", "MapReduce", "mock"),
            "language_count": ("Số sách theo nhóm ngôn ngữ", "MapReduce", "mock"),
            "category_count": ("Top category lớn", "MapReduce", "mock"),
            "avg_price_by_category": ("Giá trung bình theo category", "MapReduce", "mock"),
            "top_sold_books": ("Top 10 sách bán chạy nhất", "MapReduce", "mock"),
            "top_authors_by_sales": ("Top 10 tác giả có sách bán nhiều nhất", "MapReduce", "mock"),
            "avg_rating_by_category": ("Rating trung bình theo category", "MapReduce", "mock"),
            "top_rated_category_books": ("Sách trong category có rating trung bình cao nhất", "MapReduce", "mock"),
            "popular_books": ("Top sách phổ biến", "Spark", "mock"),
            "potential_books": ("Top sách tiềm năng", "Spark", "mock"),
            "category_performance": ("Hiệu quả category", "Spark", "mock"),
            "price_segment": ("Phân nhóm khoảng giá", "Spark", "mock"),
            "source_comparison": ("So sánh Tiki và Fahasa", "Spark", "mock"),
        }

    def analytics_chart_config(self, dataset: str) -> dict[str, str]:
        fields = {
            "source_count": ("source", "book_count"),
            "language_count": ("language_group", "book_count"),
            "category_count": ("main_category", "book_count"),
            "avg_price_by_category": ("main_category", "avg_price"),
            "top_sold_books": ("title", "sold_count"),
            "top_authors_by_sales": ("author", "total_sold"),
            "avg_rating_by_category": ("main_category", "avg_rating"),
            "top_rated_category_books": ("title", "rating"),
        }
        if dataset not in fields:
            return {}
        label_key, value_key = fields[dataset]
        return {"label_key": label_key, "value_key": value_key}

    def analytics_rows(self, dataset: str) -> tuple[str, list[dict[str, Any]]]:
        """Dữ liệu mẫu cho Analytics.

        Khi có WebHDFS thật, thay bằng đọc file trong /book_project/analytics.
        """
        data = {
            "source_count": (
                "Số sách theo nguồn",
                [
                    {"source": "tiki", "book_count": 6000},
                    {"source": "fahasa", "book_count": 4000},
                ],
            ),
            "language_count": (
                "Số sách theo nhóm ngôn ngữ",
                [
                    {"language_group": "Vietnamese", "book_count": 7300},
                    {"language_group": "English", "book_count": 2700},
                ],
            ),
            "category_count": (
                "Top category lớn",
                [
                    {"main_category": "Văn học", "book_count": 1340},
                    {"main_category": "Truyện Tranh, Manga, Comic", "book_count": 980},
                    {"main_category": "Kinh tế", "book_count": 760},
                    {"main_category": "Personal Development", "book_count": 540},
                    {"main_category": "Sách thiếu nhi", "book_count": 510},
                ],
            ),
            "avg_price_by_category": (
                "Giá trung bình theo category",
                [
                    {"main_category": "Văn học", "avg_price": 94500, "book_count": 1340},
                    {"main_category": "Kinh tế", "avg_price": 132000, "book_count": 760},
                    {"main_category": "Truyện Tranh, Manga, Comic", "avg_price": 38500, "book_count": 980},
                    {"main_category": "Personal Development", "avg_price": 174000, "book_count": 540},
                ],
            ),
            "top_sold_books": (
                "Top 10 sách bán chạy nhất",
                [
                    {"rank": 1, "book_id": "tiki_01", "source": "tiki", "title": "Nhà Giả Kim", "author": "Paulo Coelho", "main_category": "Văn học", "sold_count": 24200},
                    {"rank": 2, "book_id": "fahasa_01", "source": "fahasa", "title": "Đắc Nhân Tâm", "author": "Dale Carnegie", "main_category": "Kỹ năng sống", "sold_count": 19800},
                    {"rank": 3, "book_id": "tiki_02", "source": "tiki", "title": "Atomic Habits", "author": "James Clear", "main_category": "Personal Development", "sold_count": 12500},
                ],
            ),
            "top_authors_by_sales": (
                "Top 10 tác giả có sách bán nhiều nhất",
                [
                    {"rank": 1, "author": "Nguyễn Nhật Ánh", "total_sold": 68200, "book_count": 42},
                    {"rank": 2, "author": "Paulo Coelho", "total_sold": 41100, "book_count": 8},
                    {"rank": 3, "author": "James Clear", "total_sold": 32500, "book_count": 6},
                ],
            ),
            "avg_rating_by_category": (
                "Rating trung bình theo category",
                [
                    {"main_category": "Văn học", "avg_rating": 4.62, "rated_book_count": 810},
                    {"main_category": "Kinh tế", "avg_rating": 4.51, "rated_book_count": 430},
                    {"main_category": "Personal Development", "avg_rating": 4.74, "rated_book_count": 390},
                ],
            ),
            "top_rated_category_books": (
                "Sách trong category có rating trung bình cao nhất",
                [
                    {"main_category": "Personal Development", "category_avg_rating": 4.74, "rank": 1, "book_id": "tiki_02", "source": "tiki", "title": "Atomic Habits", "author": "James Clear", "rating": 4.9, "review_count": 5200},
                    {"main_category": "Personal Development", "category_avg_rating": 4.74, "rank": 2, "book_id": "fahasa_02", "source": "fahasa", "title": "Deep Work", "author": "Cal Newport", "rating": 4.8, "review_count": 820},
                ],
            ),
            "popular_books": (
                "Top sách phổ biến",
                [
                    {"title": "Nhà Giả Kim", "popularity_score": 98.2},
                    {"title": "Atomic Habits", "popularity_score": 96.7},
                    {"title": "Đắc Nhân Tâm", "popularity_score": 95.1},
                    {"title": "One Piece - Tập 100", "popularity_score": 91.8},
                ],
            ),
            "potential_books": (
                "Top sách tiềm năng",
                [
                    {"title": "Deep Work", "potential_score": 93.5},
                    {"title": "Educated", "potential_score": 90.7},
                    {"title": "The Psychology of Money", "potential_score": 88.2},
                ],
            ),
            "category_performance": (
                "Hiệu quả category",
                [
                    {"main_category": "Văn học", "performance_score": 88.4},
                    {"main_category": "Kinh tế", "performance_score": 84.1},
                    {"main_category": "Personal Development", "performance_score": 81.9},
                ],
            ),
            "price_segment": (
                "Phân nhóm khoảng giá",
                [
                    {"price_range": "Dưới 50.000", "book_count": 2800},
                    {"price_range": "50.000 - 100.000", "book_count": 3600},
                    {"price_range": "100.000 - 200.000", "book_count": 2500},
                    {"price_range": "Trên 200.000", "book_count": 1100},
                ],
            ),
            "source_comparison": (
                "So sánh Tiki và Fahasa",
                [
                    {"source": "tiki", "effectiveness_score": 86.2},
                    {"source": "fahasa", "effectiveness_score": 82.7},
                ],
            ),
        }
        return data.get(dataset, data["source_count"])

    def quality_rows(self) -> list[dict[str, Any]]:
        """Dữ liệu mẫu cho Data Quality; sau này thay bằng output Drill trên HDFS."""
        return [
            {"dataset": "books_landing", "total_records": 10000, "missing_required": 12, "duplicated_book_id": 5, "status": "Warning"},
            {"dataset": "books_mr", "total_records": 9995, "missing_required": 0, "duplicated_book_id": 0, "status": "OK"},
            {"dataset": "books_spark", "total_records": 9995, "missing_required": 0, "duplicated_book_id": 0, "status": "OK"},
        ]

    def list_snapshots(self) -> list[dict[str, Any]]:
        """Dữ liệu mẫu; sau này thay bằng lệnh list_snapshots của HBase."""
        return deepcopy(self.snapshots)

    def create_snapshot(self) -> str:
        """Giả lập tạo HBase Snapshot; sau này gọi script backup_hbase.sh."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"books_hbase_{timestamp}"
        self.snapshots.insert(0, {
            "name": name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "table_name": "books_hbase",
            "status": "OK",
            "note": "Mock snapshot vừa tạo",
        })
        return name

    def restore_snapshot(self, snapshot_name: str) -> str:
        """Giả lập restore; sau này gọi script restore_hbase.sh với tên snapshot hợp lệ."""
        names = {snapshot["name"] for snapshot in self.snapshots}
        if snapshot_name not in names:
            raise ValueError("Snapshot không tồn tại trong dữ liệu mẫu.")
        return snapshot_name

    def delete_snapshot(self, snapshot_name: str) -> str:
        """Giả lập xóa HBase Snapshot."""
        names = {snapshot["name"] for snapshot in self.snapshots}
        if snapshot_name not in names:
            raise ValueError("Snapshot không tồn tại trong dữ liệu mẫu.")
        self.snapshots = [
            snapshot for snapshot in self.snapshots
            if snapshot["name"] != snapshot_name
        ]
        return snapshot_name

    @staticmethod
    def _generated_books() -> list[dict[str, Any]]:
        titles = (
            "Deep Work",
            "The Psychology of Money",
            "Tuổi Trẻ Đáng Giá Bao Nhiêu",
            "Cây Cam Ngọt Của Tôi",
            "Doraemon Truyện Dài",
            "Không Gia Đình",
            "Sapiens",
            "Educated",
        )
        authors = (
            "Cal Newport",
            "Morgan Housel",
            "Rosie Nguyễn",
            "José Mauro de Vasconcelos",
            "Fujiko F. Fujio",
            "Hector Malot",
            "Yuval Noah Harari",
            "Tara Westover",
        )
        categories = (
            "Personal Development",
            "Kinh tế",
            "Tâm lý - Kỹ năng sống",
            "Văn học",
            "Truyện Tranh, Manga, Comic",
            "Văn học",
            "Lịch sử",
            "Biography",
        )
        sub_categories = (
            "Productivity",
            "Tài chính cá nhân",
            "Kỹ năng sống",
            "Tiểu thuyết",
            "Manga",
            "Văn học kinh điển",
            "Lịch sử thế giới",
            "Hồi ký",
        )
        rows = []
        for index in range(1, 27):
            item = (index - 1) % len(titles)
            source = "tiki" if index % 2 else "fahasa"
            price = 42000 + index * 3500
            rows.append({
                "book_id": f"mock-{index:03d}",
                "source": source,
                "row_key": f"{source}#mock-{index:03d}",
                "title": f"{titles[item]} - Bản mẫu {index}",
                "author": authors[item],
                "publisher": "NXB Dữ Liệu Mẫu",
                "language_group": "English" if item in {0, 1, 6, 7} else "Vietnamese",
                "main_category": categories[item],
                "sub_category": sub_categories[item],
                "price": price,
                "original_price": price + 18000,
                "discount_rate": 10,
                "rating": round(4 + (index % 10) / 10, 1),
                "review_count": index * 12,
                "sold_count": index * 145,
                "publish_year": 2018 + index % 8,
                "page_count": 180 + index * 4,
                "url": f"https://example.com/books/mock-{index:03d}",
            })
        return rows

    @staticmethod
    def _number(value: Any, default: Any = None) -> Any:
        if value in ("", None):
            return default
        try:
            number = float(value)
            return int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            return default
