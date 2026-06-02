#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: restore_hdfs.sh <snapshot_timestamp> <raw|clean|analytics|quality>" >&2
  exit 1
fi

PROJECT_ROOT_HDFS="${HDFS_PROJECT_ROOT:-/book_project}"
SNAPSHOT="$1"
SCOPE="$2"
VALID_SCOPES=(raw clean analytics quality)

if [[ ! " ${VALID_SCOPES[*]} " =~ " ${SCOPE} " ]]; then
  echo "Invalid scope: $SCOPE" >&2
  exit 1
fi
if [[ "$SNAPSHOT" == *"/"* || "$SNAPSHOT" == *".."* ]]; then
  echo "Snapshot must be a timestamp directory name." >&2
  exit 1
fi

SOURCE="$PROJECT_ROOT_HDFS/backups/$SNAPSHOT/$SCOPE"
DESTINATION="$PROJECT_ROOT_HDFS/$SCOPE"
hdfs dfs -test -e "$SOURCE"
hdfs dfs -rm -r -f "$DESTINATION"
hdfs dfs -cp "$SOURCE" "$DESTINATION"
echo "Restored $DESTINATION from $SOURCE"
