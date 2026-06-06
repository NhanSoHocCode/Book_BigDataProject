#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT_HDFS="${HDFS_PROJECT_ROOT:-/book_project}"
SCOPE="${1:-all}"
STAMP="$(date +%Y%m%d_%H%M%S)"
DESTINATION="$PROJECT_ROOT_HDFS/backups/$STAMP"
VALID_SCOPES=(raw clean analytics quality)

if [[ "$SCOPE" == "all" ]]; then
  SCOPES=("${VALID_SCOPES[@]}")
else
  SCOPES=("$SCOPE")
fi

hdfs dfs -mkdir -p "$DESTINATION"
for item in "${SCOPES[@]}"; do
  if [[ ! " ${VALID_SCOPES[*]} " =~ " ${item} " ]]; then
    echo "Invalid scope: $item" >&2
    exit 1
  fi
  hdfs dfs -test -e "$PROJECT_ROOT_HDFS/$item"
  hdfs dfs -cp "$PROJECT_ROOT_HDFS/$item" "$DESTINATION/"
done

echo "$DESTINATION"
