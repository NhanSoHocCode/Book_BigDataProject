CREATE DATABASE IF NOT EXISTS book_project;
USE book_project;

DROP TABLE IF EXISTS books_raw;
CREATE EXTERNAL TABLE books_raw (
  book_id STRING,
  source STRING,
  title STRING,
  author STRING,
  publisher STRING,
  language_group STRING,
  main_category STRING,
  sub_category STRING,
  price STRING,
  original_price STRING,
  discount_rate STRING,
  rating STRING,
  review_count STRING,
  sold_count STRING,
  publish_year STRING,
  page_count STRING,
  url STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/book_project/raw/books';

DROP TABLE IF EXISTS books_valid;
CREATE EXTERNAL TABLE books_valid (
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
  page_count INT,
  url STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/book_project/clean/books_valid';
