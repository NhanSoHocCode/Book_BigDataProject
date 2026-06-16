"""Run book analytics with Spark SQL over Hive Metastore tables."""

from __future__ import annotations

import argparse
import re

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


BOOK_COLUMNS = [
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
NUMERIC_DEFAULTS = {
    "price": 0.0,
    "original_price": 0.0,
    "discount_rate": 0.0,
    "rating": 0.0,
    "review_count": 0,
    "sold_count": 0,
}


def sql_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"Invalid Hive identifier: {name}")
    return name


def write_json(frame: DataFrame, path: str) -> None:
    frame.coalesce(1).write.mode("overwrite").json(path)


def read_hive_books(spark: SparkSession, database: str, table: str) -> DataFrame:
    source = f"{sql_name(database)}.{sql_name(table)}"
    books = spark.sql(f"SELECT {', '.join(BOOK_COLUMNS)} FROM {source}")
    return normalize_books(books)


def normalize_books(books: DataFrame) -> DataFrame:
    return books.select(
        F.col("book_id").cast("string").alias("book_id"),
        F.lower(F.trim(F.col("source").cast("string"))).alias("source"),
        F.trim(F.col("title").cast("string")).alias("title"),
        F.coalesce(F.trim(F.col("author").cast("string")), F.lit("Unknown")).alias("author"),
        F.coalesce(F.trim(F.col("publisher").cast("string")), F.lit("Unknown")).alias("publisher"),
        F.coalesce(F.trim(F.col("language_group").cast("string")), F.lit("Unknown")).alias("language_group"),
        F.coalesce(F.trim(F.col("main_category").cast("string")), F.lit("Unknown")).alias("main_category"),
        F.coalesce(F.trim(F.col("sub_category").cast("string")), F.lit("Unknown")).alias("sub_category"),
        F.col("price").cast("double").alias("price"),
        F.col("original_price").cast("double").alias("original_price"),
        F.col("discount_rate").cast("double").alias("discount_rate"),
        F.col("rating").cast("double").alias("rating"),
        F.col("review_count").cast("long").alias("review_count"),
        F.col("sold_count").cast("long").alias("sold_count"),
        F.col("publish_year").cast("int").alias("publish_year"),
        F.col("page_count").cast("long").alias("page_count"),
        F.trim(F.col("url").cast("string")).alias("url"),
    ).fillna(NUMERIC_DEFAULTS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default="book_project")
    parser.add_argument("--source-table", default="books_spark")
    parser.add_argument("--output-root", default="/book_project/analytics/spark")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("BookBigDataHiveAnalytics").enableHiveSupport().getOrCreate()
    books = read_hive_books(spark, args.database, args.source_table)

    popularity = (
        books.withColumn(
            "popularity_score",
            F.round(
                F.col("rating") * F.log1p(F.col("review_count")) +
                F.log1p(F.col("sold_count")),
                4,
            ),
        )
        .select("book_id", "source", "title", "author", "rating", "review_count", "sold_count", "popularity_score")
        .orderBy(F.desc("popularity_score"))
        .limit(100)
    )
    write_json(popularity, f"{args.output_root}/popular_books")

    potential = (
        books.filter((F.col("rating") >= 4.0) & (F.col("sold_count") <= 100))
        .withColumn(
            "potential_score",
            F.round(F.col("rating") * F.log1p(F.col("review_count") + 1) / (F.col("sold_count") + 1), 4),
        )
        .select("book_id", "source", "title", "author", "rating", "review_count", "sold_count", "potential_score")
        .orderBy(F.desc("potential_score"))
        .limit(100)
    )
    write_json(potential, f"{args.output_root}/potential_books")

    source_comparison = (
        books.groupBy("source")
        .agg(
            F.count("*").alias("book_count"),
            F.round(F.avg("price"), 2).alias("avg_price"),
            F.round(F.avg("rating"), 2).alias("avg_rating"),
            F.sum("sold_count").alias("total_sold"),
        )
        .orderBy("source")
    )
    write_json(source_comparison, f"{args.output_root}/source_comparison")

    category_performance = (
        books.groupBy("main_category")
        .agg(
            F.count("*").alias("book_count"),
            F.round(F.avg("price"), 2).alias("avg_price"),
            F.round(F.avg("rating"), 2).alias("avg_rating"),
            F.sum("sold_count").alias("total_sold"),
        )
        .orderBy(F.desc("total_sold"))
    )
    write_json(category_performance, f"{args.output_root}/category_performance")

    segmented = books.withColumn(
        "price_segment",
        F.when(F.col("price") < 100000, "under_100k")
        .when(F.col("price") < 250000, "100k_to_250k")
        .when(F.col("price") < 500000, "250k_to_500k")
        .otherwise("over_500k"),
    )
    price_segment = (
        segmented.groupBy("price_segment")
        .agg(
            F.count("*").alias("book_count"),
            F.round(F.avg("price"), 2).alias("avg_price"),
            F.round(F.avg("rating"), 2).alias("avg_rating"),
            F.sum("sold_count").alias("total_sold"),
        )
        .orderBy("price_segment")
    )
    write_json(price_segment, f"{args.output_root}/price_segment")

    spark.stop()


if __name__ == "__main__":
    main()