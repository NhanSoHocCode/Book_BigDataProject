CREATE TABLE dfs.quality.`landing_count`
AS
SELECT
    'books_landing' AS dataset,
    COUNT(*) AS total_records
FROM hive.bookbigdata.books_landing;

CREATE TABLE dfs.quality.`mr_count`
AS
SELECT
    'books_mr' AS dataset,
    COUNT(*) AS total_records
FROM hive.bookbigdata.books_mr;

CREATE TABLE dfs.quality.`spark_count`
AS
SELECT
    'books_spark' AS dataset,
    COUNT(*) AS total_records
FROM hive.bookbigdata.books_spark;

CREATE TABLE dfs.quality.`missing_required`
AS
SELECT
    COUNT(CASE WHEN book_id IS NULL THEN 1 END) AS missing_book_id,
    COUNT(CASE WHEN source IS NULL THEN 1 END) AS missing_source,
    COUNT(CASE WHEN title IS NULL THEN 1 END) AS missing_title,
    COUNT(CASE WHEN url IS NULL THEN 1 END) AS missing_url
FROM hive.bookbigdata.books_landing;

CREATE TABLE dfs.quality.`landing_vs_mr`
AS
SELECT
    ABS(
        (SELECT COUNT(*) FROM hive.bookbigdata.books_landing)
        -
        (SELECT COUNT(*) FROM hive.bookbigdata.books_mr)
    ) AS difference;

CREATE TABLE dfs.quality.`landing_vs_spark`
AS
SELECT
    ABS(
        (SELECT COUNT(*) FROM hive.bookbigdata.books_landing)
        -
        (SELECT COUNT(*) FROM hive.bookbigdata.books_spark)
    ) AS difference;

CREATE TABLE dfs.quality.`missing_in_mr`
AS
SELECT
    l.source,
    l.book_id
FROM hive.bookbigdata.books_landing l
LEFT JOIN hive.bookbigdata.books_mr m
ON l.source = m.source
AND l.book_id = m.book_id
WHERE m.book_id IS NULL;

CREATE TABLE dfs.quality.`missing_in_spark`
AS
SELECT
    l.source,
    l.book_id
FROM hive.bookbigdata.books_landing l
LEFT JOIN hive.bookbigdata.books_spark s
ON l.source = s.source
AND l.book_id = s.book_id
WHERE s.book_id IS NULL;

CREATE TABLE dfs.quality.`valid_records`
AS
SELECT COUNT(*) AS valid_records
FROM hive.bookbigdata.books_spark;

CREATE TABLE dfs.quality.`rejected_records`
AS
SELECT
    l.total - m.total AS rejected_records
FROM
(
    SELECT COUNT(*) AS total
    FROM hive.bookbigdata.books_landing
) l
CROSS JOIN
(
    SELECT COUNT(*) AS total
    FROM hive.bookbigdata.books_mr
) m;