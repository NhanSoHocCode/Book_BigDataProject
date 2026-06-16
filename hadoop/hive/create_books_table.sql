CREATE DATABASE IF NOT EXISTS bookbigdata;
USE bookbigdata;

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
	review_count INT,
	sold_count INT,
	publish_year INT,
	page_count INT,
	url STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/book_project/landing/books'; 

CREATE EXTERNAL TABLE books_mr (
	book_id STRING,
	source STRING,
	title STRING,
	author STRING,
	publisher STRING,
	language_group STRING,
	main_category STRING,
	price DOUBLE,
	rating DOUBLE,
	review_count INT,
	sold_count INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/book_project/warehouse/books_mr'; 

CREATE EXTERNAL TABLE books_spark (
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
	review_count INT,
	sold_count INT,
	publish_year INT,
    page_count INT,
	url STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/book_project/warehouse/books_spark'; 
