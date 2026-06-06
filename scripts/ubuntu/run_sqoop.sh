#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
bash "$PROJECT_ROOT/hadoop/sqoop/run_sqoop_import.sh"
