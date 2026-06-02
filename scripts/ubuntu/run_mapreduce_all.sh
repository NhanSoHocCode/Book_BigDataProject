#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MAPREDUCE_ROOT="$PROJECT_ROOT/hadoop/mapreduce"
INPUT="${HDFS_CLEAN_BOOKS:-/book_project/clean/books_valid}"
OUTPUT_ROOT="${HDFS_MAPREDUCE_OUTPUT:-/book_project/analytics/mapreduce}"

if [[ -z "${STREAMING_JAR:-}" ]]; then
  STREAMING_JAR="$(find "${HADOOP_HOME:-/usr/lib/hadoop}" -name 'hadoop-streaming*.jar' -type f -print -quit 2>/dev/null || true)"
fi
if [[ -z "$STREAMING_JAR" ]]; then
  echo "Set STREAMING_JAR to the hadoop-streaming JAR path." >&2
  exit 1
fi

run_job() {
  local job_name="$1"
  local output_name="$2"
  local reducers="${3:-1}"
  local job_directory="$MAPREDUCE_ROOT/$job_name"
  local output="$OUTPUT_ROOT/$output_name"

  hdfs dfs -rm -r -f "$output"
  hadoop jar "$STREAMING_JAR" \
    -D "mapreduce.job.name=$job_name" \
    -D "mapreduce.job.reduces=$reducers" \
    -files "$job_directory/mapper.py,$job_directory/reducer.py" \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -input "$INPUT" \
    -output "$output"
}

run_job mr01_source_count source_count
run_job mr02_language_count language_count
run_job mr03_category_count category_count
run_job mr04_author_count author_count
run_job mr05_avg_price_by_category avg_price_by_category
run_job mr06_max_price_by_category max_price_by_category
run_job mr07_top_sold_books top_sold_books 1
run_job mr08_best_seller_by_group best_seller_by_group

echo "MapReduce analytics completed: $OUTPUT_ROOT"
