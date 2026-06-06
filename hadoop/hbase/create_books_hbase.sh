#!/usr/bin/env bash
set -euo pipefail

hbase shell <<'HBASE'
disable 'books' if exists 'books'
drop 'books' if exists 'books'
create 'books', 'info', 'pricing', 'metrics'
describe 'books'
HBASE
