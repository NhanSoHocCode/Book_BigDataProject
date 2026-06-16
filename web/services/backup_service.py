from __future__ import annotations

import os
import re
import shlex
import subprocess
from datetime import datetime
from typing import Any


SNAPSHOT_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


class HBaseSnapshotService:
    def __init__(self) -> None:
        self.table = os.getenv("HBASE_TABLE", "bookbigdata:books_hbase").strip()
        self.prefix = os.getenv("HBASE_SNAPSHOT_PREFIX", "books_hbase_").strip()
        self.command = shlex.split(
            os.getenv("HBASE_SHELL_COMMAND", "hbase shell -n")
        )
        self.timeout = int(os.getenv("HBASE_COMMAND_TIMEOUT_SECONDS", "120"))

    def shell(self, statements: str) -> str:
        result = subprocess.run(
            self.command,
            input=statements,
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        if result.returncode != 0 or "ERROR" in output.upper():
            raise RuntimeError(output.strip() or "HBase Shell thực thi thất bại.")
        return output

    def list_snapshots(self) -> list[dict[str, Any]]:
        output = self.shell("list_snapshots\nexit\n")
        snapshots: list[dict[str, Any]] = []
        for line in output.splitlines():
            text = line.strip()
            if not text.startswith(self.prefix):
                continue
            parts = text.split()
            name = parts[0]
            table_name = next((part for part in parts[1:] if ":" in part), self.table)
            created_at = " ".join(parts[2:]) if len(parts) > 2 else "HBase Snapshot"
            snapshots.append({
                "name": name,
                "created_at": created_at,
                "table_name": table_name,
                "status": "OK",
                "note": "Snapshot HBase",
            })
        return sorted(snapshots, key=lambda item: item["name"], reverse=True)

    def create_snapshot(self) -> str:
        name = f"{self.prefix}{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.shell(f"snapshot '{self.table}', '{name}'\nexit\n")
        return name

    def validate_snapshot(self, snapshot_name: str) -> str:
        if (
            not snapshot_name.startswith(self.prefix)
            or not SNAPSHOT_PATTERN.fullmatch(snapshot_name)
        ):
            raise ValueError("Tên snapshot không hợp lệ.")
        snapshots = {snapshot["name"] for snapshot in self.list_snapshots()}
        if snapshot_name not in snapshots:
            raise ValueError("Snapshot không tồn tại.")
        return snapshot_name

    def restore_snapshot(self, snapshot_name: str) -> str:
        snapshot_name = self.validate_snapshot(snapshot_name)
        self.shell(f"disable '{self.table}'\nexit\n")
        try:
            self.shell(f"restore_snapshot '{snapshot_name}'\nexit\n")
        finally:
            self.shell(f"enable '{self.table}'\nexit\n")
        return snapshot_name

    def delete_snapshot(self, snapshot_name: str) -> str:
        snapshot_name = self.validate_snapshot(snapshot_name)
        self.shell(f"delete_snapshot '{snapshot_name}'\nexit\n")
        return snapshot_name

    def healthcheck(self) -> tuple[bool, str]:
        try:
            self.shell(f"exists '{self.table}'\nexit\n")
            return True, "Đã kết nối"
        except Exception as error:
            return False, str(error)