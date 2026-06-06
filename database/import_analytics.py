"""List HDFS analytics outputs.

Analytics are intentionally not imported into MySQL. This utility verifies the
WebHDFS locations that the Flask dashboard reads directly.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


PATHS = [
    "/book_project/analytics/mapreduce",
    "/book_project/analytics/spark",
    "/book_project/quality",
]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def list_status(base_url: str, user: str, path: str) -> list[dict[str, Any]]:
    response = requests.get(
        f"{base_url.rstrip('/')}/webhdfs/v1{path}",
        params={"op": "LISTSTATUS", "user.name": user},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["FileStatuses"]["FileStatus"]


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    base_url = os.getenv("HDFS_NAMENODE_URL", "http://localhost:9870")
    user = os.getenv("HDFS_USER", "hdfs")
    for path in PATHS:
        print(path)
        try:
            for item in list_status(base_url, user, path):
                print(f"  {item['type']:<9} {item['pathSuffix']}")
        except requests.RequestException as error:
            print(f"  unavailable: {error}")


if __name__ == "__main__":
    main()
