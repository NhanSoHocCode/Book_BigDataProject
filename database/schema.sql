CREATE DATABASE IF NOT EXISTS book_bigdata
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE book_bigdata;

CREATE TABLE IF NOT EXISTS books (
  book_id VARCHAR(128) NOT NULL,
  source ENUM('tiki', 'fahasa') NOT NULL,
  title TEXT NOT NULL,
  author VARCHAR(255) NOT NULL DEFAULT 'Unknown',
  publisher VARCHAR(255) NOT NULL DEFAULT 'Unknown',
  language_group VARCHAR(64) NOT NULL DEFAULT 'Unknown',
  main_category VARCHAR(255) NOT NULL DEFAULT 'Unknown',
  sub_category VARCHAR(255) NOT NULL DEFAULT 'Unknown',
  price DECIMAL(15, 2) NOT NULL DEFAULT 0,
  original_price DECIMAL(15, 2) NOT NULL DEFAULT 0,
  discount_rate DECIMAL(7, 2) NOT NULL DEFAULT 0,
  rating DECIMAL(3, 2) NOT NULL DEFAULT 0,
  review_count INT UNSIGNED NOT NULL DEFAULT 0,
  sold_count INT UNSIGNED NOT NULL DEFAULT 0,
  publish_year SMALLINT UNSIGNED NULL,
  page_count INT UNSIGNED NULL,
  url VARCHAR(1000) NOT NULL,
  PRIMARY KEY (source, book_id),

  INDEX idx_books_source (source),
  INDEX idx_books_author (author),
  INDEX idx_books_publisher (publisher),
  INDEX idx_books_category (main_category),
  INDEX idx_books_lang (language_group),
  INDEX idx_books_price (price),

  FULLTEXT INDEX idx_books_title (title) 
);