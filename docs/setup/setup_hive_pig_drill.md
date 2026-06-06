# Cài đặt Hive, Pig và Drill

## Pig và Hive

Dự án import dữ liệu sách từ MySQL vào `/book_project/raw/books`, làm sạch
bằng Pig và tạo các Hive External Table:

```bash
bash scripts/ubuntu/run_sqoop.sh
bash scripts/ubuntu/run_pig.sh
```

`run_pig.sh` chạy `hadoop/pig/clean_books.pig`, sau đó tạo:

- `book_project.books_raw`
- `book_project.books_valid`

Kiểm tra Hive:

```bash
hive -f hadoop/hive/hive_queries.sql
```

## Drill

Cấu hình Hive storage plugin của Drill để Drill có thể truy vấn các External
Table. Khởi động Drill và chạy:

```bash
bash scripts/ubuntu/run_drill.sh
```

Báo cáo chất lượng dữ liệu được lưu tại:

```text
/book_project/quality/drill_report
```
