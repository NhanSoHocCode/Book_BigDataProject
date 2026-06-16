import os
import json
import shutil
import subprocess
import pandas as pd

HDFS_QUALITY_DIR = "/book_project/quality"
LOCAL_TMP_DIR = "quality_tmp"

folders = [
    "landing_count",
    "mr_count",
    "spark_count",
    "valid_records",
    "rejected_records",
    "missing_required",
    "landing_vs_mr",
    "landing_vs_spark",
    "missing_in_mr",
    "missing_in_spark"
]

# tao thu muc tam

if os.path.exists(LOCAL_TMP_DIR):
    shutil.rmtree(LOCAL_TMP_DIR)

os.makedirs(LOCAL_TMP_DIR)

# tai file tu hdfs ve local

print("Downloading Parquet files from HDFS...")

for folder in folders:
    subprocess.run(
        [
            "hdfs",
            "dfs",
            "-get",
            f"{HDFS_QUALITY_DIR}/{folder}",
            LOCAL_TMP_DIR
        ],
        check=True
    )

print("Download completed.")

# doc parquet

def read_parquet(folder):
    path = os.path.join(LOCAL_TMP_DIR, folder)
    return pd.read_parquet(path)

# doc du lieu

landing_count = read_parquet("landing_count")
mr_count = read_parquet("mr_count")
spark_count = read_parquet("spark_count")

valid_records = read_parquet("valid_records")
rejected_records = read_parquet("rejected_records")

missing_required = read_parquet("missing_required")

landing_vs_mr = read_parquet("landing_vs_mr")
landing_vs_spark = read_parquet("landing_vs_spark")

missing_in_mr = read_parquet("missing_in_mr")
missing_in_spark = read_parquet("missing_in_spark")

# tong hop thanh json

report = {
    "datasets": {
        "books_landing": int(
            landing_count.iloc[0]["total_records"]
        ),
        "books_mr": int(
            mr_count.iloc[0]["total_records"]
        ),
        "books_spark": int(
            spark_count.iloc[0]["total_records"]
        )
    },

    "quality_checks": {
        "valid_records": int(
            valid_records.iloc[0][valid_records.columns[0]]
        ),

        "rejected_records": int(
            rejected_records.iloc[0][rejected_records.columns[0]]
        ),

        "missing_required": {
            column: int(missing_required.iloc[0][column])
            for column in missing_required.columns
        }
    },

    "reconciliation": {
        "landing_vs_mr_difference": int(
            landing_vs_mr.iloc[0]["difference"]
        ),

        "landing_vs_spark_difference": int(
            landing_vs_spark.iloc[0]["difference"]
        ),

        "missing_in_mr": len(missing_in_mr),

        "missing_in_spark": len(missing_in_spark)
    },

    "missing_records": {
        "mr": missing_in_mr.to_dict("records"),
        "spark": missing_in_spark.to_dict("records")
    }
}

# ghi ra json

with open(
    "quality_report.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        report,
        f,
        ensure_ascii=False,
        indent=4
    )

print("Generated quality_report.json")

# dua len hsfs

subprocess.run(
    [
        "hdfs",
        "dfs",
        "-put",
        "-f",
        "quality_report.json",
        HDFS_QUALITY_DIR
    ],
    check=True
)

print("Uploaded quality_report.json to HDFS.")

shutil.rmtree(LOCAL_TMP_DIR)

print("Done.")