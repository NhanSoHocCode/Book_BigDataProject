-- doc du lieu tu landing
 
raw_books = LOAD '/book_project/landing/books'
USING PigStorage('\t')
AS (
	book_id:chararray,
	source:chararray,
	title:chararray,
	author:chararray,
	publisher:chararray,
	language_group:chararray,
	main_category:chararray,
	sub_category:chararray,
	price:double,
	original_price:double,
	discount_rate:double,
	rating:double,
	review_count:int,
	sold_count:int,
	publish_year:int,
	page_count:int,
	url:chararray
);
-- chuan hoa text
 
text_clean = FOREACH raw_books GENERATE
	TRIM(book_id) AS book_id,
	LOWER(TRIM(source)) AS source,
	TRIM(title) AS title,
	TRIM(author) AS author,
	TRIM(publisher) AS publisher,
	TRIM(language_group) AS language_group,
	TRIM(main_category) AS main_category,
	TRIM(sub_category) AS sub_category,
	price AS price,
	original_price AS original_price,
	discount_rate AS discount_rate,
	rating AS rating,
	review_count AS review_count,
	sold_count AS sold_count,
	publish_year AS publish_year,
	page_count AS page_count,
	TRIM(url) AS url;
 
-- loai bo du lieu loi nghiem trong
 
valid_books = FILTER text_clean BY
	book_id IS NOT NULL
	AND book_id != ''
    AND source IS NOT NULL
	AND (source == 'tiki' OR source == 'fahasa')
	AND title IS NOT NULL
	AND title != ''
	AND url IS NOT NULL
	AND url != ''
	AND price IS NOT NULL
	AND price > 0;
 
-- chuan hoa null va gia tri bat thuong
 
normalized_books = FOREACH valid_books GENERATE
	book_id AS book_id,
	source AS source,
	title AS title,
 
	(author IS NULL OR author == '' ? 'Unknown' : author) AS author,
	(publisher IS NULL OR publisher == '' ? 'Unknown' : publisher) AS publisher,
	(language_group IS NULL OR language_group == '' ? 'Unknown' : language_group) AS language_group,
	(main_category IS NULL OR main_category == '' ? 'Unknown' : main_category) AS main_category,
	(sub_category IS NULL OR sub_category == '' ? 'Unknown' : sub_category) AS sub_category,
 
	price AS price,
 
	(original_price IS NULL OR original_price < price ? price : original_price) AS original_price,
 
	(discount_rate IS NULL OR discount_rate < 0 ? 0.0 : discount_rate) AS discount_rate,
 
	(rating IS NULL OR rating < 0 OR rating > 5 ? 0.0 : rating) AS rating,
 
	(review_count IS NULL OR review_count < 0 ? 0 : review_count) AS review_count,
 
	(sold_count IS NULL OR sold_count < 0 ? 0 : sold_count) AS sold_count,
 
	(publish_year IS NULL OR publish_year < 1900 OR publish_year > 2026 ? null : publish_year) AS publish_year,
 
	(page_count IS NULL OR page_count <= 0 ? null : page_count) AS page_count,
 
	url AS url;
 
mr_books = FOREACH normalized_books GENERATE
    book_id,
    source,
    title,
    author,
    publisher,
    language_group,
    main_category,
    price,
    rating,
    review_count,
    sold_count;
-- xuat dataset cho mapreduce và spark
 
STORE mr_books
INTO '/book_project/warehouse/books_mr'
USING PigStorage('\t');
 
STORE normalized_books
INTO '/book_project/warehouse/books_spark'
USING PigStorage('\t');