USE book_project;

SELECT source, COUNT(*) AS book_count
FROM books_valid
GROUP BY source
ORDER BY book_count DESC;

SELECT main_category, COUNT(*) AS book_count, ROUND(AVG(price), 2) AS avg_price
FROM books_valid
GROUP BY main_category
ORDER BY book_count DESC;

SELECT title, author, sold_count
FROM books_valid
ORDER BY sold_count DESC
LIMIT 20;
