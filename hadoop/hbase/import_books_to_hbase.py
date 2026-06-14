#!/usr/bin/env python3
"""Import book records from HDFS into the HBase books table.

The importer accepts JSON arrays, JSON lines, CSV, or TSV files in HDFS. Values
are written as strings so Phoenix can map the existing HBase table with VARCHAR
columns reliably.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from collections.abc import Iterable
from typing import Any


TABLE = "bookbigdata:books_hbase"

INFO_COLUMNS = [
    "source",
    "title",
    "author",
    "publisher",
    "language_group",
    "main_category",
    "sub_category",
    "publish_year",
    "page_count",
    "url",
]
PRICE_COLUMNS = ["price", "original_price", "discount_rate"]
STAT_COLUMNS = ["rating", "review_count", "sold_count"]
ALL_COLUMNS = ["book_id", *INFO_COLUMNS, *PRICE_COLUMNS, *STAT_COLUMNS]
INPUT_COLUMNS = [
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


def run_text(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        command_text = " ".join(command)
        message = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"Command failed: {command_text}\n{message}")
    return completed.stdout


def hdfs_files(path: str, hdfs_command: str) -> list[str]:
    test_exists = subprocess.run(
        [hdfs_command, "dfs", "-test", "-e", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if test_exists.returncode != 0:
        raise FileNotFoundError(f"HDFS input path does not exist: {path}")

    test_dir = subprocess.run(
        [hdfs_command, "dfs", "-test", "-d", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if test_dir.returncode != 0:
        return [path]

    output = run_text([hdfs_command, "dfs", "-ls", "-R", path])
    files: list[str] = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 8 and parts[0].startswith("-"):
            name = parts[-1]
            if not name.rsplit("/", 1)[-1].startswith(("_", ".")):
                files.append(name)
    if not files:
        raise FileNotFoundError(f"HDFS input directory has no readable data files: {path}")
    return files


def read_hdfs_file(path: str, hdfs_command: str) -> str:
    return run_text([hdfs_command, "dfs", "-cat", path])


def normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {normalize_key(str(key)): value for key, value in row.items()}


def parse_json(content: str) -> list[dict[str, Any]] | None:
    text = content.strip()
    if not text or text[0] not in "[{":
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return [normalize_row(row) for row in rows if isinstance(row, dict)]

    if isinstance(payload, list):
        return [normalize_row(row) for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        return [normalize_row(payload)]
    return []


def parse_delimited(content: str) -> list[dict[str, Any]]:
    sample = content[:4096]
    delimiter = "\t" if sample.count("\t") > sample.count(",") else ","
    rows = list(csv.reader(io.StringIO(content), delimiter=delimiter))
    if not rows:
        return []

    first_row = [normalize_key(value) for value in rows[0]]
    has_header = {"book_id", "source", "title"}.issubset(set(first_row))
    if has_header:
        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)
        return [normalize_row(row) for row in reader]

    records = []
    for row in rows:
        padded = [*row, *[""] * (len(INPUT_COLUMNS) - len(row))]
        records.append(normalize_row(dict(zip(INPUT_COLUMNS, padded[: len(INPUT_COLUMNS)]))))
    return records


def parse_records(content: str) -> list[dict[str, Any]]:
    rows = parse_json(content)
    if rows is not None:
        return rows
    return parse_delimited(content)


def clean_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    text = str(value).strip()
    if text.lower() == "null":
        return ""
    return text


def row_key(row: dict[str, Any]) -> str:
    source = clean_value(row.get("source")) or "unknown"
    book_id = clean_value(row.get("book_id") or row.get("id") or row.get("product_id"))
    if book_id:
        return f"{source}#{book_id}"

    fingerprint = hashlib.sha1(
        f"{source}|{clean_value(row.get('title'))}|{clean_value(row.get('url'))}".encode("utf-8")
    ).hexdigest()
    return f"{source}#{fingerprint}"


def ruby_quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def put_commands(row: dict[str, Any], table: str) -> Iterable[str]:
    key = row_key(row)
    for family, columns in (
        ("info", INFO_COLUMNS),
        ("price", PRICE_COLUMNS),
        ("stat", STAT_COLUMNS),
    ):
        for column in columns:
            value = clean_value(row.get(column))
            if value != "":
                yield (
                    f"put {ruby_quote(table)}, {ruby_quote(key)}, "
                    f"{ruby_quote(family + ':' + column)}, {ruby_quote(value)}"
                )


def flush(commands: list[str], hbase_command: str) -> None:
    if not commands:
        return
    payload = "\n".join(commands) + "\n"
    completed = subprocess.run(
        [hbase_command, "shell", "-n"],
        input=payload,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        output = "\n".join(
            part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
        )
        raise RuntimeError(f"HBase shell import batch failed:\n{output}")
    commands.clear()


def import_rows(args: argparse.Namespace) -> int:
    total = 0
    commands: list[str] = []
    for path in hdfs_files(args.input, args.hdfs_command):
        content = read_hdfs_file(path, args.hdfs_command)
        for row in parse_records(content):
            commands.extend(put_commands(row, args.table))
            total += 1
            if len(commands) >= args.batch_size:
                flush(commands, args.hbase_command)
                print(f"Imported {total} rows so far...", file=sys.stderr)
        print(f"Imported file: {path}", file=sys.stderr)

    flush(commands, args.hbase_command)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="Import HDFS book data into HBase.")
    parser.add_argument("--input", default="/book_project/landing/books")
    parser.add_argument("--table", default=TABLE)
    parser.add_argument("--hdfs-command", default="hdfs")
    parser.add_argument("--hbase-command", default="hbase")
    parser.add_argument("--batch-size", type=int, default=20000)
    args = parser.parse_args()

    total = import_rows(args)
    print(f"Imported {total} rows into {args.table}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Import failed: {error}", file=sys.stderr)
        sys.exit(1)
