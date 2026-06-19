from __future__ import annotations

import csv
import io
import json
import os
from typing import Any
from urllib.parse import quote

import requests


DATASETS: dict[str, dict[str, Any]] = {
    "source_count": {
        "title": "Số sách theo nguồn",
        "group": "MapReduce",
        "path": "/analytics/mapreduce/source_count",
        "format": "tsv",
        "columns": ["source", "total_books"],
        "chart_label": "source",
        "chart_value": "total_books",
        "chart_type": "pie",                
    },
    "language_count": {
        "title": "Số sách theo nhóm ngôn ngữ",
        "group": "MapReduce",
        "path": "/analytics/mapreduce/language_count",
        "format": "tsv",
        "columns": ["language_group", "total_books"],
        "chart_label": "language_group",
        "chart_value": "total_books",
        "chart_type": "doughnut",           
    },
    "category_count": {
        "title": "Số sách theo category lớn",
        "group": "MapReduce",
        "path": "/analytics/mapreduce/category_count",
        "format": "tsv",
        "columns": ["main_category", "total_books"],
        "chart_label": "main_category",
        "chart_value": "total_books",
        "chart_type": "bar",                
    },
    "avg_price_by_category": {
        "title": "Giá trung bình theo category",
        "group": "MapReduce",
        "path": "/analytics/mapreduce/avg_price_category",
        "format": "tsv",
        "columns": ["main_category", "avg_price"],
        "chart_label": "main_category",
        "chart_value": "avg_price",
        "chart_type": "horizontalBar",     
    },
    "top_sold_books": {
        "title": "Top 10 sách bán chạy nhất",
        "group": "MapReduce",
        "path": "/analytics/mapreduce/top10seller",
        "format": "tsv",
        "columns": ["title", "author", "sold_count"],
        "chart_label": "title",
        "chart_value": "sold_count",
        "chart_type": "polarArea",          
    },
    "top_authors_by_sales": {
        "title": "Top 10 tác giả có sách bán nhiều nhất",
        "group": "MapReduce",
        "path": "/analytics/mapreduce/top10author",
        "format": "tsv",
        "columns": ["author", "total_sold"],
        "chart_label": "author",
        "chart_value": "total_sold",
        "chart_type": "radar",             
    },
    "avg_rating_by_category": {
        "title": "Rating trung bình theo category",
        "group": "MapReduce",
        "path": "/analytics/mapreduce/avgRating_category",
        "format": "tsv",
        "columns": ["main_category", "avg_rating"],
        "chart_label": "main_category",
        "chart_value": "avg_rating",
        "chart_type": "bubble",            
    },
    "top_rated_category_books": {
        "title": "Sách trong category có rating trung bình cao nhất",
        "group": "MapReduce",
        "path": "/analytics/mapreduce/bestRating_cate_books",
        "format": "tsv",
        "columns": ["category", "avg_category_rating", "title", "author", "book_rating"],
        "chart_label": "category",
        "chart_value": "book_rating",
        "chart_type": "scatter",            
    },

    "popular_books": {
        "title": "Top sách phổ biến",
        "group": "Spark",
        "path": "/analytics/spark/popular_books",
        "format": "json",
        # Spark select: "book_id", "source", "title", "author", "rating", "review_count", "sold_count", "popularity_score"
        "columns": ["book_id", "source", "title", "author", "rating", "review_count", "sold_count", "popularity_score"],
        "chart_label": "title",
        "chart_value": "popularity_score",
        "chart_type": "bar",
    },
    "potential_books": {
        "title": "Top sách tiềm năng",
        "group": "Spark",
        "path": "/analytics/spark/potential_books",
        "format": "json",
        # Spark select: "book_id", "source", "title", "author", "rating", "review_count", "sold_count", "potential_score"
        "columns": ["book_id", "source", "title", "author", "rating", "review_count", "sold_count", "potential_score"],
        "chart_label": "title",
        "chart_value": "potential_score",
        "chart_type": "horizontalBar",
    },
    "source_comparison": {
        "title": "So sánh Tiki và Fahasa",
        "group": "Spark",
        "path": "/analytics/spark/source_comparison",
        "format": "json",
        # Spark agg: source, book_count, avg_price, avg_rating, total_sold
        "columns": ["source", "book_count", "avg_price", "avg_rating", "total_sold"],
        "chart_label": "source",
        "chart_value": "total_sold",
        "chart_type": "grouped_bar",        
    },
    "category_performance": {
        "title": "Hiệu quả category",
        "group": "Spark",
        "path": "/analytics/spark/category_performance",
        "format": "json",
        # Spark agg: main_category, book_count, avg_price, avg_rating, total_sold
        "columns": ["main_category", "book_count", "avg_price", "avg_rating", "total_sold"],
        "chart_label": "main_category",
        "chart_value": "total_sold",
        "chart_type": "stacked_bar",        
    },
    "price_segment": {
        "title": "Phân nhóm sách theo khoảng giá",
        "group": "Spark",
        "path": "/analytics/spark/price_segment",
        "format": "json",
        # Spark agg: price_segment, book_count, avg_price, avg_rating, total_sold
        "columns": ["price_segment", "book_count", "avg_price", "avg_rating", "total_sold"],
        "chart_label": "price_segment",
        "chart_value": "book_count",
        "chart_type": "line",               
    }
}


def scalar(value: str) -> Any:
    text = value.strip()
    if text == "":
        return ""
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return text


class HDFSService:
    def __init__(self) -> None:
        self.base_url = os.getenv("HDFS_NAMENODE_URL", "http://localhost:9870").rstrip("/")
        self.user = os.getenv("HDFS_USER", "hdfs")
        self.project_root = os.getenv("HDFS_PROJECT_ROOT", "/book_project").rstrip("/")
        self.timeout = int(os.getenv("HDFS_TIMEOUT_SECONDS", "20"))
        self.quality_report = os.getenv(
            "HDFS_QUALITY_REPORT",
            "/book_project/quality/quality_report.json",
        )

    def url(self, path: str) -> str:
        return f"{self.base_url}/webhdfs/v1{quote(path, safe='/')}"

    def list_status(self, path: str) -> list[dict[str, Any]]:
        response = requests.get(
            self.url(path),
            params={"op": "LISTSTATUS", "user.name": self.user},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["FileStatuses"]["FileStatus"]

    def file_status(self, path: str) -> dict[str, Any]:
        response = requests.get(
            self.url(path),
            params={"op": "GETFILESTATUS", "user.name": self.user},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["FileStatus"]

    def read_file(self, path: str) -> str:
        response = requests.get(
            self.url(path),
            params={"op": "OPEN", "user.name": self.user},
            timeout=self.timeout,
            allow_redirects=True,
        )
        response.raise_for_status()
        return response.text

    def read_directory(self, path: str) -> str:
        parts: list[str] = []
        for item in sorted(self.list_status(path), key=lambda value: value["pathSuffix"]):
            name = item["pathSuffix"]
            if item["type"] == "FILE" and not name.startswith(("_", ".")):
                parts.append(self.read_file(f"{path.rstrip('/')}/{name}"))
        return "\n".join(parts)

    def read_path(self, path: str) -> str:
        status = self.file_status(path)
        return self.read_file(path) if status["type"] == "FILE" else self.read_directory(path)

    def project_path(self, suffix: str) -> str:
        return f"{self.project_root}/{suffix.lstrip('/')}"

    def resolve_path(self, path: str) -> str:
        return path if path.startswith(self.project_root + "/") else self.project_path(path)

    def parse_tsv(
        self,
        content: str,
        columns: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
    
        for line in content.splitlines():
            if not line.strip():
                continue
                
            cells = [c.strip() for c in line.split("\t")]
            if not cells or cells == [""]:
                continue
                
            parsed: dict[str, Any] = {}
            
            if len(cells) == 2 and cells[1].startswith("{") and cells[1].endswith("}"):
                # Map cột đầu tiên
                first_col = columns[0] if columns else "key"
                parsed[first_col] = scalar(cells[0])
                try:
                    payload = json.loads(cells[1])
                    if isinstance(payload, dict):
                        parsed.update(payload)
                except json.JSONDecodeError:
                    second_col = columns[1] if (columns and len(columns) > 1) else "value"
                    parsed[second_col] = scalar(cells[1])
                    
            else:
                if columns:
                    for idx, col_name in enumerate(columns):
                        if idx < len(cells):
                            parsed[col_name] = scalar(cells[idx])
                        else:
                            parsed[col_name] = None # Đề phòng file bị thiếu dữ liệu hàng
                else:
                    for idx, cell_val in enumerate(cells):
                        col_name = "key" if idx == 0 else f"value_{idx}" if idx > 1 else "value"
                        parsed[col_name] = scalar(cell_val)
                        
            rows.append(parsed)
            
        return rows

    def parse_json(self, content: str) -> list[dict[str, Any]]:
        text = content.strip()
        if not text:
            return []
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return [
                row
                for line in text.splitlines()
                if line.strip()
                for row in self._json_rows(json.loads(line))
            ]
        return self._json_rows(payload)

    @staticmethod
    def _json_rows(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict):
            for key in ("rows", "results", "data", "report", "checks"):
                if isinstance(payload.get(key), list):
                    return [row for row in payload[key] if isinstance(row, dict)]
            return [payload]
        return []

    def parse_csv(self, content: str) -> list[dict[str, Any]]:
        reader = csv.DictReader(io.StringIO(content))
        return [
            {key: scalar(value or "") for key, value in row.items()}
            for row in reader
        ]

    def analytics_datasets(self) -> dict[str, tuple[str, str, str]]:
        return {
            name: (config["title"], config["group"], config["path"])
            for name, config in DATASETS.items()
        }

    def analytics_chart_config(self, name: str) -> dict[str, str]:
        config = DATASETS.get(name, {})
        return {
            key: config[value]
            for key, value in (
                ("label_key", "chart_label"),
                ("value_key", "chart_value"),
                ("chart_type", "chart_type"),           
            )
            if value in config
    }

    def read_dataset(self, name: str) -> tuple[str, list[dict[str, Any]]]:
        if name not in DATASETS:
            raise KeyError(f"Không tồn tại analytics dataset: {name}")
        config = DATASETS[name]
        content = self.read_path(self.project_path(config["path"]))
        if config["format"] == "json":
            rows = self.parse_json(content)
        elif config["format"] == "csv":
            rows = self.parse_csv(content)
        else:
            rows = self.parse_tsv(content, config.get("columns"))
        return config["title"], rows

    def read_quality_report(self) -> list[dict[str, Any]]:
        content = self.read_path(self.resolve_path(self.quality_report))
        if self.quality_report.casefold().endswith(".csv"):
            return self.parse_csv(content)
        return self.parse_json(content)

    def path_exists(self, path: str) -> bool:
        try:
            self.file_status(self.resolve_path(path))
            return True
        except Exception:
            return False

    def healthcheck(self) -> tuple[bool, str]:
        try:
            self.file_status(self.project_root)
            return True, "Đã kết nối"
        except Exception as error:
            return False, str(error)