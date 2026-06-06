#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

spark-submit \
  "$PROJECT_ROOT/hadoop/spark/book_analytics.py" \
  --table "${HIVE_BOOKS_TABLE:-book_project.books_valid}" \
  --output-root "${HDFS_SPARK_OUTPUT:-/book_project/analytics/spark}"
