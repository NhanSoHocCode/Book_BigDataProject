"""Run advanced book analytics with PySpark and write JSON Lines to HDFS."""

from __future__ import annotations

import argparse

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def write_json(frame: DataFrame, path: str) -> None:
    frame.coalesce(1).write.mode("overwrite").json(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", default="book_project.books_valid")
    parser.add_argument("--output-root", default="/book_project/analytics/spark")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("BookBigDataAnalytics").enableHiveSupport().getOrCreate()
    books = (
        spark.table(args.table)
        .fillna({"rating": 0.0, "review_count": 0, "sold_count": 0, "price": 0.0})
    )

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
        .agg(F.count("*").alias("book_count"), F.round(F.avg("price"), 2).alias("avg_price"))
        .orderBy("price_segment")
    )
    write_json(price_segment, f"{args.output_root}/price_segment")

    spark.stop()


if __name__ == "__main__":
    main()
