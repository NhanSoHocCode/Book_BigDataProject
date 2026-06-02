#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SQL_FILE="$PROJECT_ROOT/hadoop/drill/data_quality_queries.sql"
OUTPUT="${HDFS_DRILL_OUTPUT:-/book_project/quality/drill_report}"
DRILL_URL="${DRILL_URL:-jdbc:drill:zk=localhost:2181}"
TMP_FILE="$(mktemp --suffix=.csv)"
trap 'rm -f "$TMP_FILE"' EXIT

sqlline -u "$DRILL_URL" --silent=true --showHeader=true --outputformat=csv --run="$SQL_FILE" > "$TMP_FILE"
hdfs dfs -rm -r -f "$OUTPUT"
hdfs dfs -mkdir -p "$OUTPUT"
hdfs dfs -put "$TMP_FILE" "$OUTPUT/part-00000.csv"

echo "Drill quality report completed: $OUTPUT"
