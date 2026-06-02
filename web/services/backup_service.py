"""Backup and restore operations for MySQL and HDFS."""

from __future__ import annotations

import os
import shlex
import subprocess
from datetime import datetime
from pathlib import Path

from services.mysql_service import MySQLService


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HDFS_SCOPES = {"raw", "clean", "analytics", "quality"}


class BackupService:
    def __init__(self, mysql: MySQLService) -> None:
        self.mysql = mysql
        backup_directory = os.getenv("BACKUP_DIRECTORY", "backups/mysql")
        self.mysql_backup_directory = (PROJECT_ROOT / backup_directory).resolve()
        self.mysql_backup_directory.mkdir(parents=True, exist_ok=True)
        self.hdfs_root = os.getenv("HDFS_PROJECT_ROOT", "/book_project").rstrip("/")
        self.hdfs_command = shlex.split(os.getenv("HDFS_COMMAND", "hdfs"))

    def stamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def mysql_args(self) -> list[str]:
        return [
            f"--host={os.getenv('MYSQL_HOST', '127.0.0.1')}",
            f"--port={os.getenv('MYSQL_PORT', '3306')}",
            f"--user={os.getenv('MYSQL_USER', 'root')}",
            f"--password={os.getenv('MYSQL_PASSWORD', '')}",
        ]

    def backup_mysql(self) -> str:
        output = self.mysql_backup_directory / f"book_big_data_{self.stamp()}.sql"
        command = ["mysqldump", *self.mysql_args(), "--single-transaction", "--databases", os.getenv("MYSQL_DATABASE", "book_big_data")]
        try:
            with output.open("wb") as file:
                subprocess.run(command, stdout=file, check=True)
            self.mysql.log_backup("mysql", "backup", "database", str(output), "success")
            return str(output)
        except Exception as error:
            self.mysql.log_backup("mysql", "backup", "database", str(output), "failed", str(error))
            raise

    def restore_mysql(self, backup_path: str) -> str:
        path = Path(backup_path).resolve()
        if self.mysql_backup_directory not in path.parents or not path.is_file():
            raise ValueError("MySQL backup file must be inside the configured backup directory")
        command = ["mysql", *self.mysql_args()]
        try:
            with path.open("rb") as file:
                subprocess.run(command, stdin=file, check=True)
            self.mysql.log_backup("mysql", "restore", "database", str(path), "success")
            return str(path)
        except Exception as error:
            self.mysql.log_backup("mysql", "restore", "database", str(path), "failed", str(error))
            raise

    def hdfs(self, *args: str) -> None:
        subprocess.run([*self.hdfs_command, "dfs", *args], check=True)

    def backup_hdfs(self, scope: str = "all") -> str:
        scopes = sorted(HDFS_SCOPES) if scope == "all" else [scope]
        if any(item not in HDFS_SCOPES for item in scopes):
            raise ValueError("Invalid HDFS backup scope")
        destination = f"{self.hdfs_root}/backups/{self.stamp()}"
        try:
            self.hdfs("-mkdir", "-p", destination)
            for item in scopes:
                source = f"{self.hdfs_root}/{item}"
                self.hdfs("-test", "-e", source)
                self.hdfs("-cp", source, destination)
            self.mysql.log_backup("hdfs", "backup", scope, destination, "success")
            return destination
        except Exception as error:
            self.mysql.log_backup("hdfs", "backup", scope, destination, "failed", str(error))
            raise

    def restore_hdfs(self, snapshot: str, scope: str) -> str:
        if scope not in HDFS_SCOPES:
            raise ValueError("Invalid HDFS restore scope")
        if "/" in snapshot or ".." in snapshot:
            raise ValueError("Snapshot must be a timestamp directory name")
        source = f"{self.hdfs_root}/backups/{snapshot}/{scope}"
        destination = f"{self.hdfs_root}/{scope}"
        try:
            self.hdfs("-test", "-e", source)
            self.hdfs("-rm", "-r", "-f", destination)
            self.hdfs("-cp", source, destination)
            self.mysql.log_backup("hdfs", "restore", scope, source, "success")
            return source
        except Exception as error:
            self.mysql.log_backup("hdfs", "restore", scope, source, "failed", str(error))
            raise
