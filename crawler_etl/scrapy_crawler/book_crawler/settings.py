from __future__ import annotations

from pathlib import Path

from book_crawler.items import BOOK_FIELDS


BOT_NAME = "book_crawler"

SPIDER_MODULES = ["book_crawler.spiders"]
NEWSPIDER_MODULE = "book_crawler.spiders"

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

ROBOTSTXT_OBEY = False

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0 Safari/537.36 BookBigDataSystem/1.0"
)

CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 0.5
DOWNLOAD_TIMEOUT = 20

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5

RETRY_ENABLED = True
RETRY_TIMES = 2

ITEM_PIPELINES = {
    "book_crawler.pipelines.NormalizeBookFieldsPipeline": 300,
    "book_crawler.pipelines.DropDuplicateBooksPipeline": 400,
}

FEED_EXPORT_FIELDS = BOOK_FIELDS
FEED_STORE_EMPTY = False
FEEDS = {
    str(RAW_DATA_DIR / "%(name)s_books.json"): {
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
        "overwrite": True,
    }
}

LOG_LEVEL = "INFO"
