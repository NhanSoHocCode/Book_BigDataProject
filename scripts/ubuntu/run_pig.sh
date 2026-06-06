#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INPUT="${HDFS_RAW_BOOKS:-/book_project/raw/books}"
OUTPUT="${HDFS_CLEAN_BOOKS:-/book_project/clean/books_valid}"

hdfs dfs -rm -r -f "$OUTPUT"
pig \
  -param "INPUT=$INPUT" \
  -param "OUTPUT=$OUTPUT" \
  "$PROJECT_ROOT/hadoop/pig/clean_books.pig"

hive -f "$PROJECT_ROOT/hadoop/hive/create_books_table.sql"
