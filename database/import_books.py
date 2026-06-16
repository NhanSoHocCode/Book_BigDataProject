import pandas as pd
import mysql.connector

CSV_FILE = r"D:\BDE\Project\BookBigDataSystem\data\clean\books_clean.csv"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "natsume0705",
    "database": "book_bigdata",
}

FIELDS = [
    "book_id", "source", "title", "author", "publisher",
    "language_group", "main_category", "sub_category",
    "price", "original_price", "discount_rate", "rating",
    "review_count", "sold_count", "publish_year", "page_count", "url"
]

def clean_text(value, default="Unknown"):
    if pd.isna(value) or str(value).strip() == "":
        return default
    return str(value).strip()

def clean_float(value, default=0.0):
    if pd.isna(value) or value == "":
        return default
    return float(value)

def clean_int(value, default=0):
    if pd.isna(value) or value == "":
        return default
    return int(float(value))

def clean_nullable_int(value):
    if pd.isna(value) or value == "":
        return None
    return int(float(value))

def main():
    df = pd.read_csv(CSV_FILE)

    missing_cols = [col for col in FIELDS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"CSV thiếu cột: {missing_cols}")

    df = df[FIELDS]

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    sql = """
    INSERT INTO books (
        book_id, source, title, author, publisher,
        language_group, main_category, sub_category,
        price, original_price, discount_rate, rating,
        review_count, sold_count, publish_year, page_count, url
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        title = VALUES(title),
        author = VALUES(author),
        publisher = VALUES(publisher),
        language_group = VALUES(language_group),
        main_category = VALUES(main_category),
        sub_category = VALUES(sub_category),
        price = VALUES(price),
        original_price = VALUES(original_price),
        discount_rate = VALUES(discount_rate),
        rating = VALUES(rating),
        review_count = VALUES(review_count),
        sold_count = VALUES(sold_count),
        publish_year = VALUES(publish_year),
        page_count = VALUES(page_count),
        url = VALUES(url)
    """

    count = 0

    try:
        for _, row in df.iterrows():
            values = (
                clean_text(row["book_id"], default=""),
                clean_text(row["source"], default="unknown").lower(),
                clean_text(row["title"], default="Unknown"),
                clean_text(row["author"], default="Unknown"),
                clean_text(row["publisher"], default="Unknown"),
                clean_text(row["language_group"], default="Unknown"),
                clean_text(row["main_category"], default="Unknown"),
                clean_text(row["sub_category"], default="Unknown"),
                clean_float(row["price"]),
                clean_float(row["original_price"]),
                clean_float(row["discount_rate"]),
                clean_float(row["rating"]),
                clean_int(row["review_count"]),
                clean_int(row["sold_count"]),
                clean_nullable_int(row["publish_year"]),
                clean_nullable_int(row["page_count"]),
                clean_text(row["url"], default=""),
            )

            cursor.execute(sql, values)
            count += 1

        conn.commit()
        print(f"Imported/Updated {count} rows successfully.")

    except Exception as e:
        conn.rollback()
        print("Import failed.")
        print(e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()