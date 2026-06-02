#!/usr/bin/env bash
set -euo pipefail

MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_DATABASE="${MYSQL_DATABASE:-book_big_data}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-}"
HDFS_RAW_BOOKS="${HDFS_RAW_BOOKS:-/book_project/raw/books}"

PASSWORD_ARGS=(--password "$MYSQL_PASSWORD")
if [[ -n "${SQOOP_PASSWORD_FILE:-}" ]]; then
  PASSWORD_ARGS=(--password-file "$SQOOP_PASSWORD_FILE")
fi

sqoop import \
  --connect "jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}?useSSL=false&serverTimezone=UTC" \
  --username "$MYSQL_USER" \
  "${PASSWORD_ARGS[@]}" \
  --table books \
  --columns "book_id,source,title,author,publisher,language_group,main_category,sub_category,price,original_price,discount_rate,rating,review_count,sold_count,publish_year,page_count,url" \
  --target-dir "$HDFS_RAW_BOOKS" \
  --delete-target-dir \
  --fields-terminated-by $'\t' \
  --lines-terminated-by $'\n' \
  --null-string '' \
  --null-non-string '' \
  --num-mappers 1

echo "Sqoop import completed: ${HDFS_RAW_BOOKS}"
