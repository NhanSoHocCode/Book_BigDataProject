#!/usr/bin/env bash
set -euo pipefail

sqoop import \
--connect jdbc:mysql://localhost:3306/book_bigdata \
--username root \
-P \
--query "SELECT book_id, source, title, author, publisher, language_group, main_category, sub_category, price, original_price, discount_rate, rating, review_count, sold_count, publish_year, page_count, url FROM books WHERE \$CONDITIONS" \
--target-dir /book_project/landing/books \
--fields-terminated-by '\t' \
--lines-terminated-by '\n' \
--num-mappers 1