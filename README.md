# Book Big Data Analytics System

## Lưu ý đầu:

Code/Script/Nội dung ở các file chỉ ở mức THAM KHẢO, cần tìm hiểu và điều chỉnh cho ổn hơn.

## 1. Tổng quan

**Book Big Data Analytics System** là hệ thống thu thập, lưu trữ, xử lý và
phân tích dữ liệu sách từ hai nguồn **Tiki** và **Fahasa**.

Dữ liệu sau khi crawl được chuẩn hóa về một schema chung, lưu vào MySQL, đưa
lên HDFS bằng Apache Sqoop và xử lý bằng các công cụ trong Hadoop Ecosystem.
Kết quả phân tích được giữ trên HDFS để Web Flask đọc trực tiếp và hiển thị.

## 2. Chuẩn bị môi trường và cài đặt

### 2.1. Bộ phiên bản đề xuất

Không nên tự chọn bản mới nhất của từng công cụ vì các thành phần trong Hadoop
Ecosystem cần tương thích với nhau. Toàn bộ nhóm nên cài cùng một baseline:

| Công cụ | Phiên bản đề xuất | Ghi chú |
| --- | --- | --- |
| OpenJDK | `11` | Dùng chung cho Hadoop và các thành phần chạy JVM |
| MySQL Server | `8.4.x LTS` | Lưu dữ liệu sách và lịch sử backup |
| MySQL Connector/J | `8.4.0` | JDBC driver để Sqoop kết nối MySQL |
| Apache Hadoop | `3.3.6` | Cung cấp HDFS, YARN và MapReduce |
| Apache Sqoop | `1.4.7` | Dự án đã retired; chỉ dùng để minh họa import MySQL vào HDFS |
| Apache Pig | `0.18.0` | Làm sạch dữ liệu trên HDFS |
| Apache Hive | `4.0.1` | Tương thích với Hadoop `3.3.6` |
| Apache Spark / PySpark | `3.5.8` | Dùng nhánh Spark `3.5` để phân tích nâng cao |
| Apache Drill | `1.22.0` | Truy vấn báo cáo Data Quality |
| Apache HBase | `2.6.3` | Chọn gói `hadoop3-bin` |
| Apache Phoenix | `5.3.0` | Chọn gói tương ứng với HBase `2.6` |
| Apache ZooKeeper | `3.8.6` | Nhánh stable để điều phối HBase |


### 2.2. Máy Windows phát triển Web, Crawler và ETL

Cài các công cụ sau:

| Công cụ | Phiên bản | Mục đích | Link chính thức |
| --- | --- | --- | --- |
| MySQL Server | `8.4.x LTS` | Lưu dữ liệu sách và lịch sử backup | [MySQL Installer for Windows](https://dev.mysql.com/downloads/installer/) |
| MySQL Workbench | `8.0.x` | Quản trị MySQL bằng giao diện | [Download MySQL Workbench](https://dev.mysql.com/downloads/workbench/) |

Sau khi clone dự án, chạy trong thư mục gốc:

```bat
pip install -r requirements.txt
copy .env.example .env
```

Các thư viện Python được khai báo trong `requirements.txt`:

| Thư viện | Vai trò |
| --- | --- |
| `beautifulsoup4`, `lxml` | Parse HTML khi crawl Fahasa |
| `requests` | Gọi Tiki API và WebHDFS REST API |
| `flask` | Xây dựng Web |
| `mysql-connector-python` | Kết nối Flask và script import với MySQL |
| `python-dotenv` | Đọc cấu hình từ file `.env` |

Mở `.env`, cập nhật tài khoản MySQL và địa chỉ NameNode. Sau khi ETL tạo
`books_clean.csv`, khởi tạo schema và import dữ liệu:

```bat
scripts\windows\run_crawl_etl.bat
scripts\windows\import_mysql.bat
scripts\windows\run_web.bat
```

Web chạy mặc định tại `http://127.0.0.1:5000`.

### 2.3. Máy ảo Ubuntu và cluster Hadoop

| Công cụ | Phiên bản | Link chính thức |
| --- | --- | --- |
| Apache Hadoop | `3.3.6` | [Apache Hadoop Releases](https://hadoop.apache.org/releases) |
| Apache Pig | `0.18.0` | [Apache Pig Releases](https://pig.apache.org/releases.html) |
| Apache Hive | `4.0.1` | [Apache Hive Downloads](https://hive.apache.org/downloads.html) |
| Apache Drill | `1.22.0` | [Install Apache Drill](https://drill.apache.org/docs/install-drill/) |
| Apache Spark | `3.5.8` | [Apache Spark Downloads](https://spark.apache.org/downloads.html) |
| Apache HBase | `2.6.3` `hadoop3-bin` | [Apache HBase Downloads](https://hbase.apache.org/downloads/) |
| Apache Phoenix | `5.3.0` cho HBase `2.6` | [Apache Phoenix Downloads](https://phoenix.apache.org/download) |
| Apache ZooKeeper | `3.8.6` stable | [Apache ZooKeeper Releases](https://zookeeper.apache.org/releases.html) |
| Apache Sqoop | `1.4.7` | [Apache Sqoop Attic](https://attic.apache.org/projects/sqoop.html) |
| MySQL Connector/J | `8.4.0` | [Download Connector/J](https://dev.mysql.com/downloads/connector/j/) |

Cài các package nền trên mỗi node Ubuntu:

```bash
sudo apt update
sudo apt install -y openssh-server openssh-client rsync python3 curl mysql-client
```

Cài Java `11` trên mỗi node:

```bash
sudo apt install -y openjdk-11-jdk
java -version
```

Sau khi cài Hadoop `3.3.6`, bật HDFS và YARN, kiểm tra các daemon:

```bash
start-dfs.sh
start-yarn.sh
jps
hdfs dfs -mkdir -p /book_project
hdfs dfs -ls /
```

Sao chép file JAR của MySQL Connector/J vào thư mục `lib` của Sqoop. Cấu hình
WebHDFS trên NameNode theo hướng dẫn tại `docs/setup/setup_hadoop.md`.

### 2.4. Cấu hình kết nối Flask với MySQL và HDFS

Sao chép `.env.example` thành `.env`, sau đó sửa các giá trị theo môi trường
thực tế. File `.env.example` là file mẫu được commit lên Git; file `.env` chứa
thông tin riêng của máy và không được commit.

```text
HDFS_NAMENODE_URL=http://<namenode-host>:<webhdfs-port>
HDFS_USER=<hdfs-user>
HDFS_PROJECT_ROOT=/book_project
MYSQL_HOST=<mysql-host>
MYSQL_PORT=3306
MYSQL_DATABASE=book_big_data
MYSQL_USER=<mysql-user>
MYSQL_PASSWORD=<mysql-password>
```

Các script Python và Flask đọc trực tiếp file `.env`. Khi chạy script Bash
trên Ubuntu, cần export các biến tương ứng trong terminal hoặc khai báo trong
`~/.bashrc`.

### 2.5. Phân biệt thư mục hướng dẫn, mã xử lý và script chạy

| Thư mục | Vai trò | Khi nào sử dụng |
| --- | --- | --- |
| `docs/setup/` | Tài liệu hướng dẫn cài đặt và cấu hình thủ công | Đọc khi dựng môi trường lần đầu hoặc xử lý lỗi cấu hình |
| `hadoop/` | Mã xử lý thật: truy vấn SQL, Pig script, mapper, reducer và PySpark | Được các script Ubuntu gọi sau khi môi trường đã cài xong |
| `scripts/ubuntu/` | Script điều phối pipeline trên máy ảo Ubuntu | Chạy sau khi Hadoop Ecosystem đã hoạt động |
| `scripts/windows/` | Script chạy Crawler, ETL, import MySQL và Flask trên Windows | Chạy trên máy phát triển Windows |

Các file trong `scripts/ubuntu/` không cài Hadoop tự động. Chúng chỉ gom các
lệnh vận hành để chạy đúng thứ tự:

| File | Chức năng |
| --- | --- |
| `run_sqoop.sh` | Import bảng `books` từ MySQL vào HDFS |
| `run_pig.sh` | Làm sạch dữ liệu trên HDFS và tạo Hive External Table |
| `run_mapreduce_all.sh` | Chạy lần lượt 8 job Hadoop Streaming |
| `run_spark.sh` | Chạy phân tích nâng cao bằng PySpark |
| `run_drill.sh` | Tạo báo cáo Data Quality bằng Drill |
| `run_hbase_phoenix.sh` | Chạy luồng demo HBase và Phoenix |
| `backup_hdfs.sh` | Sao lưu các vùng dữ liệu quan trọng trên HDFS |
| `restore_hdfs.sh` | Khôi phục dữ liệu HDFS từ bản backup |

Các file trong `scripts/windows/` hỗ trợ luồng chạy local trên Windows:

| File | Chức năng |
| --- | --- |
| `run_crawl_etl.bat` | Crawl dữ liệu Tiki và Fahasa, sau đó chạy ETL |
| `import_mysql.bat` | Khởi tạo schema và import `books_clean.csv` vào MySQL |
| `run_web.bat` | Khởi động Flask Web tại `http://127.0.0.1:5000` |

Các file trong `docs/setup/` là tài liệu để đọc, không phải script để chạy:

| File | Nội dung |
| --- | --- |
| `setup_windows.md` | Cài môi trường Python, MySQL và chạy Flask trên Windows |
| `setup_ubuntu_cluster.md` | Chuẩn bị các node Ubuntu và biến môi trường chung |
| `setup_hadoop.md` | Cấu hình HDFS, YARN, WebHDFS và Hadoop Streaming |
| `setup_hive_pig_drill.md` | Cấu hình Pig, Hive External Table và Drill |
| `setup_spark.md` | Cấu hình Spark/PySpark và kiểm tra output |
| `setup_hbase_phoenix_zookeeper.md` | Cấu hình luồng NoSQL demo |

### 2.6. Chạy pipeline Hadoop trên Ubuntu

Phần này thực hiện trong máy ảo sau khi đã cài và kiểm tra môi trường. Trước
khi chạy, cần xem từng script để cập nhật địa chỉ host, tài khoản và đường dẫn
cài đặt thực tế của cluster.

Chạy theo thứ tự:

```bash
bash scripts/ubuntu/run_sqoop.sh
bash scripts/ubuntu/run_pig.sh
bash scripts/ubuntu/run_mapreduce_all.sh
bash scripts/ubuntu/run_spark.sh
bash scripts/ubuntu/run_drill.sh
```

Demo HBase và Phoenix là bước tùy chọn:

```bash
bash scripts/ubuntu/run_hbase_phoenix.sh
```

Xem hướng dẫn chi tiết trong thư mục `docs/setup`.

## 3. Mục tiêu hệ thống

- Thu thập dữ liệu sách từ hai nguồn: Tiki và Fahasa.
- Crawl Tiki bằng API JSON.
- Crawl Fahasa bằng HTML từ trang danh mục và trang chi tiết sản phẩm.
- Chuẩn hóa dữ liệu từ hai nguồn khác cấu trúc về một schema chung.
- Lưu dữ liệu sách vào MySQL để phục vụ CRUD, tìm kiếm và lọc.
- Đưa dữ liệu từ MySQL lên HDFS bằng Apache Sqoop.
- Làm sạch dữ liệu trên HDFS bằng Apache Pig.
- Tạo lớp Data Warehouse bằng Apache Hive.
- Phân tích dữ liệu bằng MapReduce và Spark/PySpark.
- Kiểm tra chất lượng dữ liệu bằng Apache Drill.
- Minh họa lưu trữ NoSQL bằng HBase, Phoenix và ZooKeeper.
- Giữ kết quả phân tích trên HDFS và cho Web Flask đọc trực tiếp bằng WebHDFS
  API.
- Hiển thị dữ liệu, bảng phân tích, biểu đồ và báo cáo chất lượng dữ liệu trên
  Web Flask.
- Hỗ trợ backup và restore dữ liệu MySQL.
- Hỗ trợ backup và restore dữ liệu trên HDFS.

## 4. Kiến trúc tổng thể

```text
Tiki API + Fahasa HTML
        |
        v
Crawler + ETL
        |
        v
books_clean.csv
        |
        v
MySQL
        |
        v
Flask Web
        |
        v
CRUD / Search / Filter / Backup / Restore

MySQL
        |
        v
Sqoop
        |
        v
HDFS
        |
        v
Pig
        |
        v
books_valid
        |
        v
Hive Data Warehouse
        |
        v
MapReduce / Spark / Drill
        |
        v
HDFS Analytics & Quality Results
        |
        v
WebHDFS API
        |
        v
Flask Web Analytics / Data Quality

HDFS Data & Analytics Results
        |
        v
HDFS Backup / Restore
```

## 5. Nguồn dữ liệu

### 5.1. Tiki

Dữ liệu Tiki được crawl bằng API:

```text
https://tiki.vn/api/personalish/v1/blocks/listings
```

Nhóm dữ liệu:

- Sách tiếng Việt.
- English Books.

Các trường dữ liệu được thu thập:

- `book_id`
- `title`
- `author`
- `language_group`
- `main_category`
- `sub_category`
- `price`
- `original_price`
- `discount_rate`
- `rating`
- `review_count`
- `sold_count`
- `url`

### 5.2. Fahasa

Dữ liệu Fahasa được crawl bằng HTML từ các trang danh mục:

```text
https://www.fahasa.com/sach-trong-nuoc.html
https://www.fahasa.com/foreigncategory.html
```

Quy trình:

- Crawl trang danh mục để lấy danh sách sản phẩm.
- Crawl trang chi tiết để lấy thông tin chi tiết của từng sách.

Các trường dữ liệu được thu thập:

- `book_id`
- `title`
- `author`
- `publisher`
- `language_group`
- `main_category`
- `sub_category`
- `price`
- `original_price`
- `discount_rate`
- `rating`
- `sold_count`
- `publish_year`
- `page_count`
- `url`

## 6. Schema chung sau ETL

```text
book_id
source
title
author
publisher
language_group
main_category
sub_category
price
original_price
discount_rate
rating
review_count
sold_count
publish_year
page_count
url
```

## 7. Các thành phần chính

### 7.1. Crawler và ETL

- Thu thập dữ liệu từ Tiki và Fahasa.
- Lưu dữ liệu thô thành JSON.
- Chuẩn hóa dữ liệu về schema chung.
- Làm sạch dữ liệu.
- Xử lý giá trị `NULL`.
- Chuẩn hóa kiểu dữ liệu.
- Chuẩn hóa category.
- Xuất file `books_clean.csv`.

### 7.2. MySQL

- Là cơ sở dữ liệu chính của hệ thống Web.
- Lưu dữ liệu sách sau ETL.
- Phục vụ chức năng CRUD.
- Phục vụ tìm kiếm và lọc dữ liệu.
- Không lưu kết quả phân tích MapReduce và Spark. Các kết quả này được giữ
  trên HDFS.
- Lưu lịch sử backup và restore của MySQL và HDFS.
- Hỗ trợ backup và restore dữ liệu MySQL.

### 7.3. Flask Web

Chức năng quản lý sách:

- Xem danh sách sách.
- Thêm, sửa và xóa sách.
- Tìm kiếm sách.
- Lọc theo nguồn, category, tác giả, nhà xuất bản và khoảng giá.

Chức năng phân tích dữ liệu:

- Hiển thị kết quả MapReduce.
- Hiển thị kết quả Spark/PySpark.
- Đọc trực tiếp kết quả phân tích trên HDFS bằng WebHDFS API.
- Đặt logic truy cập HDFS trong `web/services/hdfs_service.py`.
- Hiển thị bảng và biểu đồ bằng Chart.js.

Chức năng Data Quality:

- Hiển thị kết quả kiểm tra chất lượng dữ liệu từ Drill được lưu trên HDFS.

Chức năng Backup & Restore:

- Backup MySQL.
- Restore MySQL.
- Backup dữ liệu HDFS.
- Restore dữ liệu HDFS.
- Xem lịch sử backup.

### 7.4. Sqoop

- Đưa dữ liệu từ MySQL lên HDFS.
- Lưu dữ liệu sau khi import tại:

```text
/book_project/raw/books
```

### 7.5. Pig

- Làm sạch dữ liệu trên HDFS.
- Loại bỏ record lỗi.
- Chuẩn hóa dữ liệu.
- Tạo tập dữ liệu hợp lệ tại:

```text
/book_project/clean/books_valid
```

### 7.6. Hive

- Đóng vai trò Data Warehouse Layer trên HDFS.
- Tạo External Table từ dữ liệu `books_valid`.
- Quản lý metadata dữ liệu sách trên Hadoop.
- Cung cấp dữ liệu đầu vào cho Spark/PySpark.
- Không trực tiếp đảm nhiệm chức năng hiển thị chính trên Web.

### 7.7. MapReduce

MapReduce được viết bằng Python thông qua Hadoop Streaming. Hệ thống gồm 8 job
với độ phức tạp tăng dần từ phép đếm, tính trung bình, tìm cực trị đến Top-N và
phân tích nhiều nhóm:

| Job | Bài toán | Vai trò phân tích |
| --- | --- | --- |
| `mr01_source_count` | Đếm số sách theo nguồn | Kiểm tra phân bố dữ liệu giữa Tiki và Fahasa |
| `mr02_language_count` | Đếm số sách theo nhóm ngôn ngữ | So sánh sách tiếng Việt và sách ngoại văn |
| `mr03_category_count` | Đếm số sách theo category lớn | Xác định nhóm sách phổ biến |
| `mr04_author_count` | Đếm số sách theo tác giả | Tìm tác giả có danh mục sách phong phú |
| `mr05_avg_price_by_category` | Tính giá trung bình theo category | So sánh mặt bằng giá giữa các thể loại |
| `mr06_max_price_by_category` | Tìm sách giá cao nhất theo category | Minh họa phép tìm cực trị và giữ metadata sách |
| `mr07_top_sold_books` | Tìm top sách bán chạy nhất | Phân tích xếp hạng Top-N toàn hệ thống |
| `mr08_best_seller_by_group` | Tìm sách bán nhiều nhất theo tác giả, nhà xuất bản và category | Phân tích nhiều loại key và tìm cực trị theo từng nhóm |

Mỗi job có cấu trúc thống nhất:

```text
hadoop/mapreduce/<job_name>/
|-- mapper.py
`-- reducer.py
```

Kết quả được lưu trên HDFS và hiển thị trên Web dưới dạng bảng và biểu đồ.
Flask đọc trực tiếp các file kết quả bằng WebHDFS API.

### 7.8. Spark / PySpark

Spark/PySpark thực hiện các bài toán phân tích nâng cao:

- Tính điểm phổ biến của sách.
- Tìm sách tiềm năng.
- So sánh dữ liệu giữa Tiki và Fahasa.
- Phân tích hiệu quả category.
- Phân nhóm sách theo khoảng giá.

Kết quả được lưu trên HDFS. Flask đọc trực tiếp các file kết quả bằng WebHDFS
API và hiển thị biểu đồ bằng Chart.js.

### 7.9. Drill

Drill kiểm tra và đối soát chất lượng dữ liệu trên HDFS thông qua các truy vấn:

- Tổng số record.
- Số record hợp lệ.
- Số record bị loại.
- Số record thiếu `title`.
- Số record thiếu `price`.
- Số record thiếu `publisher`.
- Số record thiếu `review_count`.

Kết quả được lưu trên HDFS. Flask đọc các file báo cáo bằng WebHDFS API và
hiển thị trong mục Data Quality.

### 7.10. HDFS Backup & Restore

- Backup các vùng dữ liệu quan trọng trên HDFS theo thời điểm.
- Lưu bản sao trong thư mục `/book_project/backups/<timestamp>`.
- Hỗ trợ restore từng nhóm dữ liệu: raw, clean, analytics hoặc quality.
- Ghi lịch sử thao tác backup và restore vào bảng `backup_logs` trong MySQL.
- Sử dụng các lệnh `hdfs dfs` trong script Ubuntu để sao chép và khôi phục dữ
  liệu.
- Đặt script backup tại `scripts/ubuntu/backup_hdfs.sh`.
- Đặt script restore tại `scripts/ubuntu/restore_hdfs.sh`.

Các vùng dữ liệu cần backup:

```text
/book_project/raw
/book_project/clean
/book_project/analytics
/book_project/quality
```

### 7.11. HBase, Phoenix và ZooKeeper

**HBase**

- Lưu trữ dữ liệu sách dưới dạng NoSQL Column-Family.
- Minh họa khả năng lưu trữ dữ liệu phân tán trong Hadoop Ecosystem.

**Phoenix**

- Cho phép truy vấn dữ liệu HBase bằng SQL.

**ZooKeeper**

- Điều phối hoạt động của HBase trong môi trường cluster.

Nhóm công cụ này dùng để minh họa tích hợp NoSQL trong Hadoop Ecosystem,
không phải chức năng chính của Web.

## 8. Lưu trữ kết quả phân tích trên HDFS

Kết quả MapReduce, Spark/PySpark và Drill không cần đưa ngược về các bảng
analytics trong MySQL. Web Flask đọc trực tiếp file kết quả từ HDFS bằng
WebHDFS API.

Cấu trúc thư mục đề xuất:

```text
/book_project/
|-- raw/
|   `-- books/
|-- clean/
|   `-- books_valid/
|-- analytics/
|   |-- mapreduce/
|   |   |-- source_count/
|   |   |-- language_count/
|   |   |-- category_count/
|   |   |-- author_count/
|   |   |-- avg_price_by_category/
|   |   |-- max_price_by_category/
|   |   |-- top_sold_books/
|   |   `-- best_seller_by_group/
|   `-- spark/
|       |-- popular_books/
|       |-- potential_books/
|       |-- source_comparison/
|       |-- category_performance/
|       `-- price_segment/
|-- quality/
|   `-- drill_report/
`-- backups/
    `-- <timestamp>/
```

Nên xuất kết quả phân tích ở định dạng JSON hoặc CSV để Flask dễ đọc và
chuyển thành dữ liệu cho Chart.js. HDFS phù hợp để lưu và đọc các kết quả tổng
hợp có kích thước vừa phải. Nếu dashboard được truy cập thường xuyên hoặc dữ
liệu lớn, nên thêm cache tại Flask để giảm số lần đọc HDFS.

## 9. Các bảng MySQL chính

- `books`
- `backup_logs`

`backup_logs` lưu lịch sử backup và restore của cả MySQL và HDFS.

## 10. Cấu trúc Web

Menu chính gồm:

- Quản lý sách.
- Phân tích dữ liệu.
- Data Quality.
- Backup & Restore.

## 11. Công nghệ sử dụng

- Python
- Flask
- Bootstrap
- Chart.js
- MySQL
- Hadoop HDFS
- Sqoop
- Pig
- Hive
- Drill
- MapReduce
- Spark/PySpark
- HBase
- Phoenix
- ZooKeeper

## 12. Phân công công việc

### 12.1. Công việc chung của toàn bộ thành viên

Mọi người đề phải cài đặt, cấu hình và kiểm thử môi trường
Hadoop Ecosystem gồm Ubuntu Cluster, HDFS, YARN, Sqoop, Pig, Hive, Drill,
Spark, HBase, Phoenix và ZooKeeper.

Các file tài liệu và cấu hình dùng chung:

```text
README.md
.env.example
requirements.txt
docs/setup/
```

### 12.2. Phân công theo module


| Thành viên | Phần phụ trách | Nội dung thực hiện | File và thư mục chính |
| --- | --- | --- | --- |
| `<Tên thành viên>` | Crawl + ETL | Khảo sát Tiki và Fahasa; crawl Tiki bằng API; crawl Fahasa bằng HTML và trang detail; lưu raw JSON; chuẩn hóa schema; validate dữ liệu; xuất `books_clean.csv`. | `crawler_etl/config/`, `crawler_etl/crawlers/`, `crawler_etl/etl/`, `scripts/windows/run_crawl_etl.bat`, `data/raw/`, `data/clean/` |
| `<Tên thành viên>` | Flask Web | CRUD sách từ MySQL; search, filter và phân trang; giao diện Bootstrap; biểu đồ Chart.js; đọc analytics và Data Quality trực tiếp từ HDFS bằng WebHDFS; giao diện backup và restore. | `web/app.py`, `web/routes/`, `web/services/`, `web/templates/`, `web/static/`, `scripts/windows/run_web.bat` |
| `<Tên thành viên>` | MySQL + Hadoop nền | Thiết kế schema MySQL; import CSV; phối hợp dựng Ubuntu cluster, HDFS và YARN; cấu hình Sqoop, Pig, Hive; tạo External Table; triển khai script backup và restore MySQL, HDFS; điều phối tích hợp pipeline nền. | `database/`, `hadoop/sqoop/`, `hadoop/pig/`, `hadoop/hive/`, `scripts/windows/import_mysql.bat`, `scripts/ubuntu/run_sqoop.sh`, `scripts/ubuntu/run_pig.sh`, `scripts/ubuntu/backup_hdfs.sh`, `scripts/ubuntu/restore_hdfs.sh`, `docs/setup/setup_hadoop.md`, `docs/setup/setup_ubuntu_cluster.md` |
| `<Tên thành viên>` | Phân tích 1: MapReduce + Data Quality | Viết 8 job Hadoop Streaming; thiết kế output chuẩn cho Web; viết truy vấn Drill kiểm tra dữ liệu NULL, thiếu field, record hợp lệ và record bị loại; tạo báo cáo Data Quality trên HDFS. | `hadoop/mapreduce/`, `hadoop/drill/data_quality_queries.sql`, `scripts/ubuntu/run_mapreduce_all.sh`, `scripts/ubuntu/run_drill.sh`, `docs/setup/setup_hive_pig_drill.md` |
| `<Tên thành viên>` | Phân tích 2: Spark/PySpark + HBase/Phoenix/ZooKeeper | Viết PySpark phân tích nâng cao; tạo output JSON trên HDFS cho Web đọc; cài đặt và cấu hình module NoSQL demo; thiết kế bảng HBase; import dữ liệu mẫu; viết truy vấn Phoenix. | `hadoop/spark/`, `hadoop/hbase/`, `hadoop/phoenix/`, `scripts/ubuntu/run_spark.sh`, `scripts/ubuntu/run_hbase_phoenix.sh`, `docs/setup/setup_spark.md`, `docs/setup/setup_hbase_phoenix_zookeeper.md` |

### 12.3. Contract tích hợp giữa các module

Cần thống nhất và không tự ý thay đổi các contract sau:

- Schema chung gồm 17 cột theo mục 6.
- Dữ liệu raw và clean trên HDFS dùng TSV.
- Output MapReduce dùng TSV; output Spark dùng JSON Lines.
- Đường dẫn HDFS bắt đầu từ `/book_project`.
- Flask đọc analytics và Data Quality từ HDFS bằng WebHDFS API.

## 13. Kết quả cuối cùng

Hệ thống hoàn chỉnh cho phép nhóm thu thập dữ liệu sách từ internet, chuẩn hóa
dữ liệu, lưu trữ vào MySQL, đưa dữ liệu lên Hadoop để xử lý và phân tích, sau
đó giữ kết quả trên HDFS và hiển thị trực tiếp trên Web dưới dạng bảng và biểu
đồ thông qua WebHDFS API. Hệ thống hỗ trợ backup và restore cho cả MySQL và
HDFS.
