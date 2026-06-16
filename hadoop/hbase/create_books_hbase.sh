#!/usr/bin/env bash
set -euo pipefail

hbase shell <<'HBASE'
create_namespace 'bookbigdata' unless list_namespace.include?('bookbigdata')
create 'bookbigdata:books_hbase', 'info', 'price', 'stat' unless exists 'bookbigdata:books_hbase'
describe 'bookbigdata:books_hbase'
HBASE
