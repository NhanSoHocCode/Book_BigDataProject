#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

HIVE_DATABASE="${HIVE_DATABASE:-book_project}"

HIVE_SPARK_SOURCE_TABLE="${HIVE_SPARK_SOURCE_TABLE:-books_spark}"
HDFS_SPARK_OUTPUT="${HDFS_SPARK_OUTPUT:-/book_project/analytics/spark}"

if ! command -v spark-submit >/dev/null 2>&1; then
  echo "spark-submit not found in PATH." >&2
  exit 1
fi

spark-submit \
  "$PROJECT_ROOT/hadoop/spark/book_analytics.py" \
  --database "$HIVE_DATABASE" \
  --source-table "$HIVE_SPARK_SOURCE_TABLE" \
  --output-root "$HDFS_SPARK_OUTPUT"
