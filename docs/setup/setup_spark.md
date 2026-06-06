# Cài đặt Spark

Cài Apache Spark `3.5.8` có hỗ trợ Hive và bảo đảm gọi được `spark-submit`
thông qua biến `PATH`.

PySpark đã nằm trong bản phân phối Apache Spark. Pipeline Ubuntu không cần
chạy riêng `pip install pyspark` khi sử dụng `spark-submit`.

Nếu muốn kiểm thử Spark local, cài thêm Python package PySpark `3.5.8`:

```bash
python3 -m pip install -r requirements-spark.txt
```

Giữ phiên bản PySpark local tương thích với phiên bản Spark được cài trên
cluster.

Ứng dụng Spark đọc bảng `book_project.books_valid` và ghi kết quả JSON Lines
vào `/book_project/analytics/spark`.

Chạy:

```bash
bash scripts/ubuntu/run_spark.sh
```

Kiểm tra:

```bash
hdfs dfs -ls /book_project/analytics/spark
hdfs dfs -cat /book_project/analytics/spark/source_comparison/part-*
```
