CREATE DATABASE IF NOT EXISTS book_big_data
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE book_big_data;

CREATE TABLE IF NOT EXISTS books (
  book_id VARCHAR(128) NOT NULL,
  source ENUM('tiki', 'fahasa') NOT NULL,
  title VARCHAR(500) NOT NULL,
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
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (source, book_id),
  INDEX idx_books_title (title),
  INDEX idx_books_author (author),
  INDEX idx_books_publisher (publisher),
  INDEX idx_books_category (main_category),
  INDEX idx_books_price (price)
);

CREATE TABLE IF NOT EXISTS backup_logs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  storage_type ENUM('mysql', 'hdfs') NOT NULL,
  action_type ENUM('backup', 'restore') NOT NULL,
  scope_name VARCHAR(128) NOT NULL,
  backup_path VARCHAR(1000) NOT NULL,
  status ENUM('success', 'failed') NOT NULL,
  message TEXT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_backup_logs_created_at (created_at)
);
