%default INPUT '/book_project/raw/books'
%default OUTPUT '/book_project/clean/books_valid'

raw_books = LOAD '$INPUT' USING PigStorage('\t') AS (
  book_id:chararray,
  source:chararray,
  title:chararray,
  author:chararray,
  publisher:chararray,
  language_group:chararray,
  main_category:chararray,
  sub_category:chararray,
  price:chararray,
  original_price:chararray,
  discount_rate:chararray,
  rating:chararray,
  review_count:chararray,
  sold_count:chararray,
  publish_year:chararray,
  page_count:chararray,
  url:chararray
);

valid_books = FILTER raw_books BY
  book_id IS NOT NULL AND TRIM(book_id) != '' AND
  source IS NOT NULL AND TRIM(source) != '' AND
  title IS NOT NULL AND TRIM(title) != '' AND
  price IS NOT NULL AND price MATCHES '[0-9]+(\\.[0-9]+)?' AND
  url IS NOT NULL AND TRIM(url) != '';

clean_books = FOREACH valid_books GENERATE
  TRIM(book_id),
  LOWER(TRIM(source)),
  TRIM(title),
  (author IS NULL OR TRIM(author) == '' ? 'Unknown' : TRIM(author)),
  (publisher IS NULL OR TRIM(publisher) == '' ? 'Unknown' : TRIM(publisher)),
  (language_group IS NULL OR TRIM(language_group) == '' ? 'Unknown' : TRIM(language_group)),
  (main_category IS NULL OR TRIM(main_category) == '' ? 'Unknown' : TRIM(main_category)),
  (sub_category IS NULL OR TRIM(sub_category) == '' ? 'Unknown' : TRIM(sub_category)),
  (double)price,
  (double)(original_price IS NULL OR original_price == '' ? price : original_price),
  (double)(discount_rate IS NULL OR discount_rate == '' ? '0' : discount_rate),
  (double)(rating IS NULL OR rating == '' ? '0' : rating),
  (long)(review_count IS NULL OR review_count == '' ? '0' : review_count),
  (long)(sold_count IS NULL OR sold_count == '' ? '0' : sold_count),
  (publish_year IS NULL OR publish_year == '' ? '' : publish_year),
  (page_count IS NULL OR page_count == '' ? '' : page_count),
  TRIM(url);

STORE clean_books INTO '$OUTPUT' USING PigStorage('\t');
