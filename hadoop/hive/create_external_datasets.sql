CREATE DATABASE IF NOT EXISTS book_project;
USE book_project;

DROP TABLE IF EXISTS books_landing;
CREATE EXTERNAL TABLE books_landing (
  book_id STRING,
  source STRING,
  title STRING,
  author STRING,
  publisher STRING,
  language_group STRING,
  main_category STRING,
  sub_category STRING,
  price DOUBLE,
  original_price DOUBLE,
  discount_rate DOUBLE,
  rating DOUBLE,
  review_count BIGINT,
  sold_count BIGINT,
  publish_year INT,
  page_count BIGINT,
  url STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/book_project/landing/books';
