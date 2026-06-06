SELECT 'total_records' AS metric, COUNT(*) AS metric_value
FROM hive.book_project.books_raw
UNION ALL
SELECT 'valid_records' AS metric, COUNT(*) AS metric_value
FROM hive.book_project.books_valid
UNION ALL
SELECT 'rejected_records' AS metric,
  raw.total_records - valid.valid_records AS metric_value
FROM (SELECT COUNT(*) AS total_records FROM hive.book_project.books_raw) raw
CROSS JOIN (SELECT COUNT(*) AS valid_records FROM hive.book_project.books_valid) valid
UNION ALL
SELECT 'missing_title' AS metric, COUNT(*) AS metric_value
FROM hive.book_project.books_raw
WHERE title IS NULL OR TRIM(title) = ''
UNION ALL
SELECT 'missing_price' AS metric, COUNT(*) AS metric_value
FROM hive.book_project.books_raw
WHERE price IS NULL OR TRIM(price) = ''
UNION ALL
SELECT 'missing_publisher' AS metric, COUNT(*) AS metric_value
FROM hive.book_project.books_raw
WHERE publisher IS NULL OR TRIM(publisher) = ''
UNION ALL
SELECT 'missing_review_count' AS metric, COUNT(*) AS metric_value
FROM hive.book_project.books_raw
WHERE review_count IS NULL OR TRIM(review_count) = '';
