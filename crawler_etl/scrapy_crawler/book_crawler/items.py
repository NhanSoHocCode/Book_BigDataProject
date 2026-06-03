from __future__ import annotations

import scrapy


BOOK_FIELDS = [
    "book_id",
    "source",
    "title",
    "author",
    "publisher",
    "language_group",
    "main_category",
    "sub_category",
    "price",
    "original_price",
    "discount_rate",
    "rating",
    "review_count",
    "sold_count",
    "publish_year",
    "page_count",
    "url",
]


class BookItem(scrapy.Item):
    book_id = scrapy.Field()
    source = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    publisher = scrapy.Field()
    language_group = scrapy.Field()
    main_category = scrapy.Field()
    sub_category = scrapy.Field()
    price = scrapy.Field()
    original_price = scrapy.Field()
    discount_rate = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    sold_count = scrapy.Field()
    publish_year = scrapy.Field()
    page_count = scrapy.Field()
    url = scrapy.Field()
