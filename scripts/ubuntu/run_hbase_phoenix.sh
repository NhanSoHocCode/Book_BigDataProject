#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PHOENIX_SQLLINE="${PHOENIX_SQLLINE:-sqlline.py}"
PHOENIX_ZK="${PHOENIX_ZK:-localhost:2181}"

bash "$PROJECT_ROOT/hadoop/hbase/create_books_hbase.sh"
"$PHOENIX_SQLLINE" "$PHOENIX_ZK" "$PROJECT_ROOT/hadoop/phoenix/phoenix_queries.sql"

if ! jps | grep -q "ThriftServer"; then
  hbase-daemon.sh start thrift
fi

echo "HBase table, Phoenix mapped view and HBase Thrift Server are ready."
