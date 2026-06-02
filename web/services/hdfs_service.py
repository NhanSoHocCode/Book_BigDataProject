"""Read analytics and quality result files from HDFS through WebHDFS."""

from __future__ import annotations

import csv
import io
import json
import os
from typing import Any
from urllib.parse import quote

import requests


DATASETS = {
    "source_count": ("MapReduce: books by source", "/analytics/mapreduce/source_count", "tsv"),
    "language_count": ("MapReduce: books by language", "/analytics/mapreduce/language_count", "tsv"),
    "category_count": ("MapReduce: books by category", "/analytics/mapreduce/category_count", "tsv"),
    "author_count": ("MapReduce: books by author", "/analytics/mapreduce/author_count", "tsv"),
    "avg_price_by_category": ("MapReduce: average price by category", "/analytics/mapreduce/avg_price_by_category", "tsv"),
    "max_price_by_category": ("MapReduce: maximum price by category", "/analytics/mapreduce/max_price_by_category", "tsv"),
    "top_sold_books": ("MapReduce: top sold books", "/analytics/mapreduce/top_sold_books", "tsv"),
    "best_seller_by_group": ("MapReduce: best seller by group", "/analytics/mapreduce/best_seller_by_group", "tsv"),
    "popular_books": ("Spark: popular books", "/analytics/spark/popular_books", "jsonl"),
    "potential_books": ("Spark: potential books", "/analytics/spark/potential_books", "jsonl"),
    "source_comparison": ("Spark: source comparison", "/analytics/spark/source_comparison", "jsonl"),
    "category_performance": ("Spark: category performance", "/analytics/spark/category_performance", "jsonl"),
    "price_segment": ("Spark: price segment", "/analytics/spark/price_segment", "jsonl"),
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
        for item in self.list_status(path):
            name = item["pathSuffix"]
            if item["type"] == "FILE" and not name.startswith(("_", ".")):
                parts.append(self.read_file(f"{path.rstrip('/')}/{name}"))
        return "\n".join(parts)

    def project_path(self, suffix: str) -> str:
        return f"{self.project_root}/{suffix.lstrip('/')}"

    def parse_tsv(self, content: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for line in content.splitlines():
            if not line.strip():
                continue
            cells = line.split("\t")
            parsed: dict[str, Any] = {}
            if cells and cells[-1].lstrip().startswith("{"):
                try:
                    payload = json.loads(cells[-1])
                    cells = cells[:-1]
                    if isinstance(payload, dict):
                        parsed.update(payload)
                except json.JSONDecodeError:
                    pass
            for index, cell in enumerate(cells, start=1):
                parsed[f"key_{index}" if index < len(cells) else "value"] = scalar(cell)
            rows.append(parsed)
        return rows

    def parse_jsonl(self, content: str) -> list[dict[str, Any]]:
        return [json.loads(line) for line in content.splitlines() if line.strip()]

    def read_dataset(self, name: str) -> tuple[str, list[dict[str, Any]]]:
        if name not in DATASETS:
            raise KeyError(f"Unknown analytics dataset: {name}")
        title, suffix, file_format = DATASETS[name]
        content = self.read_directory(self.project_path(suffix))
        rows = self.parse_jsonl(content) if file_format == "jsonl" else self.parse_tsv(content)
        return title, rows

    def read_quality_report(self) -> list[dict[str, Any]]:
        content = self.read_directory(self.project_path("/quality/drill_report"))
        reader = csv.DictReader(io.StringIO(content))
        return [{key: scalar(value) for key, value in row.items()} for row in reader]
