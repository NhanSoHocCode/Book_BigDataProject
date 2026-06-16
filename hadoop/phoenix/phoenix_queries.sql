-- Yêu cầu phoenix.schema.isNamespaceMappingEnabled=true.
-- View đầu tiên ánh xạ trực tiếp bảng HBase vật lý và giữ đúng tên chữ thường.
CREATE VIEW IF NOT EXISTS "bookbigdata"."books_hbase" (
  ROW_KEY VARCHAR NOT NULL PRIMARY KEY,
  "info"."source" VARCHAR,
  "info"."title" VARCHAR,
  "info"."author" VARCHAR,
  "info"."publisher" VARCHAR,
  "info"."language_group" VARCHAR,
  "info"."main_category" VARCHAR,
  "info"."sub_category" VARCHAR,
  "info"."publish_year" VARCHAR,
  "info"."page_count" VARCHAR,
  "info"."url" VARCHAR,
  "price"."price" VARCHAR,
  "price"."original_price" VARCHAR,
  "price"."discount_rate" VARCHAR,
  "stat"."rating" VARCHAR,
  "stat"."review_count" VARCHAR,
  "stat"."sold_count" VARCHAR
);

CREATE SCHEMA IF NOT EXISTS BOOKBIGDATA;

-- Alias SQL dùng cho Web. Parent view ánh xạ trực tiếp HBase nên view này read-only.
CREATE VIEW IF NOT EXISTS BOOKBIGDATA.BOOKS
AS SELECT * FROM "bookbigdata"."books_hbase"
WHERE ROW_KEY IS NOT NULL;

SELECT "info"."main_category", COUNT(*) AS BOOK_COUNT
FROM BOOKBIGDATA.BOOKS
GROUP BY "info"."main_category"
ORDER BY BOOK_COUNT DESC;
