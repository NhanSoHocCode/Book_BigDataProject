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
Ecosystem cần tương thích với nhau. Dự án hiện triển khai theo mô hình
**WSL Ubuntu single node / pseudo-distributed**, vì vậy toàn bộ nhóm nên cài
cùng một baseline:

| Công cụ | Phiên bản đề xuất | Ghi chú |
| --- | --- | --- |
| OpenJDK | `11` | Dùng chung cho Hadoop và các thành phần chạy JVM |
| MySQL Server | `8.4.x LTS` | Cài trong WSL, dùng làm staging cho Sqoop |
| MySQL Connector/J | `8.4.0` | JDBC driver để Sqoop kết nối MySQL |
| Apache Hadoop | `3.3.6` | Cung cấp HDFS, YARN và MapReduce |
| Apache Sqoop | `1.4.7` | Import MySQL vào HDFS |
| Apache Pig | `0.18.0` | Tiền xử lý dataset trên HDFS |
| Apache Hive | `4.0.1` | Tương thích với Hadoop `3.3.6` |
| Apache Spark / PySpark | `3.5.8` | Dùng nhánh Spark `3.5` để phân tích nâng cao |
| Apache Drill | `1.22.0` | Truy vấn báo cáo Data Quality |
| Apache HBase | `2.6.3` | Chọn gói `hadoop3-bin` |
| Apache Phoenix | `5.3.0` | Chọn gói tương ứng với HBase `2.6` |
| Apache ZooKeeper | `3.8.6` | Nhánh stable để điều phối HBase |

### 2.2. Cài Python và chạy crawler/ETL trong WSL

Trong thư mục gốc dự án:

```bash
pip install -r requirements.txt
```

Các thư viện Python được khai báo trong `requirements.txt`:

| Thư viện | Vai trò |
| --- | --- |
| `requests` | Gọi Tiki API và WebHDFS REST API |
| `flask` | Xây dựng Web |
| `happybase` | Thực hiện thêm, cập nhật và xóa dữ liệu trực tiếp trên HBase qua Thrift Server |
| `JayDeBeApi`, `JPype1` | Kết nối Phoenix JDBC thick client để chạy `SELECT` và `EXPLAIN` từ Flask trong WSL |
| `mysql-connector-python` | Kết nối script import với MySQL trong WSL |
| `python-dotenv` | Đọc cấu hình từ file `.env` |
| `scrapy` | Crawl dữ liệu Tiki và Fahasa bằng spider |

### 2.3. Cài Hadoop Ecosystem trên WSL single node

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

Cài các package nền trong WSL:

```bash
sudo apt update
sudo apt install -y openssh-server openssh-client rsync curl mysql-server mysql-client
```

Cài Java `11`:

```bash
sudo apt install -y openjdk-11-jdk
java -version
```

## 3. Mục tiêu hệ thống

- Thu thập dữ liệu sách từ hai nguồn: Tiki và Fahasa.
- Crawl Tiki bằng API JSON và trang chi tiết sản phẩm bằng HTML.
- Crawl Fahasa bằng HTML từ trang danh mục và trang chi tiết sản phẩm.
- Chuẩn hóa dữ liệu từ hai nguồn khác cấu trúc về một schema chung.
- Lưu dữ liệu sách vào MySQL để đưa lên HDFS.
- Đưa dữ liệu từ MySQL lên HDFS bằng Apache Sqoop.
- Sử dụng Apache Pig để tạo các dataset chuyên biệt trên HDFS phục vụ MapReduce và Spark/PySpark.
- Tạo lớp Data Warehouse bằng Apache Hive thông qua External Table quản lý metadata các dataset trên HDFS.
- Phân tích dữ liệu sách bằng Hadoop MapReduce và Spark/PySpark.
- Kiểm tra chất lượng và đối soát dữ liệu giữa các dataset bằng Apache Drill.
- Import dữ liệu sách từ HDFS vào HBase dưới dạng NoSQL Column-Family.
- Tạo Phoenix View ánh xạ với bảng HBase để Flask hiển thị danh sách, tìm kiếm, lọc, phân trang và truy vấn SQL.
- Sử dụng HappyBase và HBase Thrift Server để Flask thêm, cập nhật và xóa dữ liệu trực tiếp trên HBase.
- Lưu kết quả phân tích và báo cáo Data Quality trên HDFS để Web Flask đọc và hiển thị.
- Hiển thị danh sách sách, chức năng quản lý dữ liệu, bảng phân tích, biểu đồ và báo cáo chất lượng dữ liệu trên Web Flask.
- Hỗ trợ backup và restore dữ liệu HBase bằng HBase Snapshot.
- Triển khai Hadoop Ecosystem trên WSL Ubuntu single node theo mô hình pseudo-distributed để thuận tiện cài đặt, kiểm thử và demo.

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
MySQL trong WSL
        |
        v
Sqoop
        |
        v
HDFS Landing Dataset
        |
        +--------------------+
        |                    |
        v                    v
Import vào HBase        Pig tạo dataset phân tích
        |                    |
        +-------------+      +----------------------+
        |             |      |                      |
        v             v      v                      v
Phoenix View     HBase Thrift / HappyBase      books_mr     books_spark
        |             |                              |                 |
        v             v                              v                 v
Flask JDBC SELECT/Search  Flask CRUD             MapReduce       Hive External Table
        |             |                              |                 |
        +------+------+                              v                 v
               |                                HDFS Analytics   Spark/PySpark
               v                                                       |
       HBase Snapshot Backup                                          v
                                                                 HDFS Analytics

Drill đọc Landing, books_mr và books_spark
        |
        v
HDFS Data Quality Reports
        |
        v
Flask Web Analytics / Data Quality
```

## 5. Nguồn dữ liệu

### 5.1. Tiki

Dữ liệu Tiki được crawl chủ yếu bằng API danh sách sản phẩm:

```text
https://tiki.vn/api/personalish/v1/blocks/listings
```

Crawler có thể lấy thêm thông tin cần thiết từ trang chi tiết sản phẩm khi API
danh sách không cung cấp đủ dữ liệu.

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
- `publisher` nếu lấy được từ dữ liệu chi tiết
- `url`

### 5.2. Fahasa

Dữ liệu Fahasa được crawl bằng Scrapy từ các trang danh mục và trang chi tiết:

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
- `review_count`
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

- Thu thập dữ liệu từ Tiki và Fahasa bằng Scrapy.
- Lưu dữ liệu thô thành JSON.
- Chuẩn hóa dữ liệu về schema chung.
- Làm sạch và chuẩn hóa dữ liệu ở mức local.
- Xử lý giá trị `NULL`.
- Chuẩn hóa kiểu dữ liệu.
- Chuẩn hóa category.
- Xuất file `books_clean.csv`.

### 7.2. MySQL

- Cài trong WSL và dùng như staging database.
- Nhận dữ liệu từ `books_clean.csv`.
- Cung cấp bảng `books` để Apache Sqoop import lên HDFS.
- Không còn là cơ sở dữ liệu chính cho Web CRUD.
- Không lưu kết quả phân tích MapReduce, Spark hoặc Drill.

### 7.3. Sqoop

- Đưa dữ liệu từ MySQL staging lên HDFS.
- Lưu dữ liệu landing sau khi import tại:

```text
/book_project/landing/books
```

### 7.4. HDFS

- Lưu dữ liệu landing được Sqoop import từ MySQL.
- Lưu các dataset do Pig tạo cho MapReduce và Spark.
- Lưu output phân tích của MapReduce và Spark/PySpark.
- Lưu báo cáo Data Quality do Drill tạo.
- Cung cấp dữ liệu cho Flask thông qua WebHDFS API.

### 7.5. Pig

Pig không làm sạch lại toàn bộ dữ liệu vì Python ETL đã xử lý phần này ở local.
Pig được dùng để tiền xử lý dữ liệu trên HDFS và tạo các dataset chuyên biệt:

```text
/book_project/warehouse/books_mr
/book_project/warehouse/books_spark
```

Dataset `books_mr` có dạng TSV phẳng, gồm các cột cần thiết cho Hadoop
Streaming như `book_id`, `source`, `title`, `language_group`, `main_category`,
`author`, `publisher`, `price` và `sold_count`.

Dataset `books_spark` giữ nhiều thuộc tính hơn để Spark/PySpark thực hiện các
phân tích nâng cao như điểm phổ biến, sách tiềm năng và hiệu quả category.

### 7.6. Hive

- Đóng vai trò Data Warehouse Layer trên HDFS.
- Tạo External Table cho dữ liệu landing, dataset MapReduce và dataset Spark.
- Quản lý schema, kiểu dữ liệu, định dạng file và đường dẫn HDFS.
- Cung cấp bảng dữ liệu đầu vào thống nhất cho Spark/PySpark.
- Hỗ trợ kiểm tra dữ liệu bằng HiveQL.

Các bảng dự kiến:

```text
books_landing
books_mr
books_spark
```

### 7.7. MapReduce

MapReduce được viết bằng Python thông qua Hadoop Streaming. Hệ thống gồm 8 job
phục vụ so sánh nguồn dữ liệu, phân tích category, giá, rating và xu hướng bán:

| Job | Bài toán | Vai trò phân tích |
| --- | --- | --- |
| `mr01_source_count` | Đếm số sách theo nguồn | Kiểm tra phân bố dữ liệu giữa Tiki và Fahasa |
| `mr02_language_count` | Đếm số sách theo nhóm ngôn ngữ | So sánh sách tiếng Việt và sách ngoại văn |
| `mr03_category_count` | Đếm số sách theo category lớn | Xác định nhóm sách phổ biến |
| `mr04_avg_price_by_category` | Tính giá trung bình theo category | Phân tích phân khúc giá |
| `mr05_top_sold_books` | Tìm Top 10 sách bán chạy nhất | Phân tích xu hướng mua toàn hệ thống |
| `mr06_top_authors_by_sales` | Tìm Top 10 tác giả có tổng số sách bán nhiều nhất | Xác định tác giả có sức hút thị trường |
| `mr07_avg_rating_by_category` | Tính rating trung bình theo category | Xác định category được đánh giá tốt |
| `mr08_top_rated_category_books` | Tìm category có rating trung bình cao nhất và danh sách sách trong category | Đi sâu vào category được yêu thích nhất |

Mỗi job có cấu trúc thống nhất:

```text
hadoop/mapreduce/<job_name>/
|-- mapper.py
`-- reducer.py
```

MapReduce đọc trực tiếp dataset `books_mr` trên HDFS. Mỗi job dùng một reducer
và lưu kết quả tại `result.csv` để Web đọc bằng WebHDFS API.

### 7.8. Spark / PySpark

Spark/PySpark thực hiện các bài toán phân tích nâng cao:

- Tính điểm phổ biến của sách.
- Tạo bảng top sách tiềm năng.
- Phân tích hiệu quả category.
- Phân nhóm sách theo khoảng giá.
- So sánh hiệu quả giữa Tiki và Fahasa.

Spark có thể đọc dataset thông qua Hive External Table `books_spark` hoặc đọc
trực tiếp từ HDFS. Kết quả được lưu trên HDFS để Flask hiển thị bằng bảng và biểu đồ Chart.js.

### 7.9. Drill

Apache Drill được dùng để kiểm tra chất lượng và đối soát dữ liệu trực tiếp trên HDFS.

Drill truy vấn các Hive External Table books_landing, books_mr và books_spark để đối soát dữ liệu.

```text
books_landing
books_mr
books_spark
```

Các nhóm kiểm tra chính:

- Tổng số bản ghi trong từng dataset.
- Số lượng sách theo nguồn và nhóm ngôn ngữ.
- Bản ghi thiếu các trường bắt buộc.
- `book_id` bị trùng hoặc bị mất giữa các dataset.
- Giá trị không hợp lệ ở các cột như `price`, `rating`, `sold_count`.
- So sánh số lượng bản ghi giữa dataset landing và các dataset do Pig tạo.
- Tạo báo cáo Data Quality tổng hợp và chi tiết.

Kết quả Drill được lưu trên HDFS và hiển thị trong mục Data Quality của Web.

### 7.10. HBase, Phoenix và ZooKeeper

**ZooKeeper**

- Điều phối HBase trong môi trường WSL single node.
- Quản lý trạng thái HBase Master và RegionServer.

**HBase**

- Lưu dữ liệu sách dưới dạng NoSQL Column-Family.
- Tạo namespace `bookbigdata` và bảng `bookbigdata:books_hbase`.
- Bảng sử dụng ba Column Family: `info`, `price` và `stat`.
- Dữ liệu được import từ HDFS landing vào bảng `bookbigdata:books_hbase`.
- Dữ liệu import vào HBase được lưu ở dạng chuỗi để dễ ánh xạ bằng Phoenix View.
- Là nơi phục vụ chính cho các chức năng quản lý sách trên Web.
- Khởi chạy HBase Thrift Server để Flask thực hiện thêm, cập nhật và xóa thông qua HappyBase.
- Hỗ trợ backup và restore bằng HBase Snapshot.

**Phoenix**

- Tạo mapped View `"bookbigdata"."books_hbase"` ánh xạ trực tiếp với bảng HBase vật lý.
- Tạo View read-only `BOOKBIGDATA.BOOKS` làm tên truy vấn thống nhất cho Flask.
- Phoenix View ánh xạ trực tiếp bảng HBase là read-only.
- Cho phép Flask thực hiện `SELECT`, hiển thị danh sách, tìm kiếm, lọc, phân trang và truy vấn SQL.
- Bật namespace mapping để mapped View `"bookbigdata"."books_hbase"` ánh xạ đúng bảng HBase `bookbigdata:books_hbase`:

```xml
<property>
  <name>phoenix.schema.isNamespaceMappingEnabled</name>
  <value>true</value>
</property>
```

- Flask chạy trong WSL và kết nối Phoenix bằng JDBC thick client thông qua `JayDeBeApi`/`JPype1`, không cần Phoenix Query Server.

**HappyBase**

- Kết nối Flask với HBase thông qua HBase Thrift Server.
- Thực hiện thêm và cập nhật sách bằng `put`.
- Thực hiện xóa sách bằng `delete`.
- Sử dụng RowKey có dạng `source#book_id`.

Khởi chạy Thrift Server trước khi chạy Flask ở chế độ live:

```bash
hbase-daemon.sh start thrift
jps
```

`jps` cần hiển thị tiến trình `ThriftServer`.

### 7.11. Flask Web

Chức năng quản lý sách:

- Xem danh sách và chi tiết sách từ HBase thông qua Phoenix View.
- Tìm kiếm, lọc, sắp xếp và phân trang bằng Phoenix SQL.
- Thêm, sửa và xóa sách trực tiếp trên HBase thông qua HappyBase.
- Lọc theo nguồn, category, tác giả, nhà xuất bản và khoảng giá.
- Cung cấp trang nhập truy vấn `SELECT` để kiểm tra dữ liệu HBase.

Chức năng phân tích dữ liệu:

- Hiển thị kết quả MapReduce.
- Hiển thị kết quả Spark/PySpark.
- Đọc kết quả phân tích trên HDFS bằng WebHDFS API.
- Đặt logic truy cập HDFS trong `web/services/hdfs_service.py`.
- Hiển thị bảng và biểu đồ bằng Chart.js.

Chức năng Data Quality:

- Hiển thị báo cáo Data Quality từ Drill được lưu trên HDFS.

Chức năng Backup & Restore:

- Tạo HBase Snapshot.
- Liệt kê các snapshot hiện có.
- Restore hoặc clone snapshot được chọn.
- Xóa snapshot không còn cần thiết sau bước xác nhận.
- Hiển thị trạng thái backup và restore.

## 8. Lưu trữ dữ liệu trên HDFS và HBase

HDFS lưu dữ liệu batch, dataset phân tích và kết quả báo cáo. HBase lưu dữ
liệu sách phục vụ Web. Phoenix View đảm nhiệm truy vấn đọc, còn HappyBase đảm
nhiệm thêm, cập nhật và xóa trực tiếp trên HBase.

Cấu trúc HDFS đề xuất:

```text
/book_project/
|-- landing/
|   `-- books/
|-- warehouse/
|   |-- books_m
|   |
|   `-- books_spark
|
|-- analytics/
|   |-- mapreduce/
|   |   |-- source_count/
|   |   |-- language_count/
|   |   |-- category_count/
|   |   |-- avg_price_by_category/
|   |   |-- top_sold_books/
|   |   |-- top_authors_by_sales/
|   |   |-- avg_rating_by_category/
|   |   `-- top_rated_category_books/
|   `-- spark/
|       |-- popular_books/
|       |-- potential_books/
|       |-- source_comparison/
|       |-- category_performance/
|       `-- price_segment/
|-- quality/
|   `-- quality_report.json

/hbase/\
|-- data/
    `-- bookbigdata/books_hbase
```

Cấu trúc HBase/Phoenix đề xuất:

```text
HBase table: bookbigdata:books_hbase
Phoenix mapped view: "bookbigdata"."books_hbase"
Phoenix web view: BOOKBIGDATA.BOOKS
RowKey: source#book_id
Column-Family:
|-- info
|-- price
`-- stat
```

Kết quả MapReduce được lưu dưới dạng CSV; kết quả Spark/PySpark và Drill được
lưu dưới dạng JSON để Flask dễ đọc và chuyển thành dữ liệu cho Chart.js.

## 9. Bảng, dataset và view chính

### 9.1. MySQL

- `books`: bảng staging để Sqoop import lên HDFS.

### 9.2. HDFS/Hive

- `books_landing`: dữ liệu từ MySQL sau khi Sqoop import.
- `books_mr`: dataset do Pig tạo cho Hadoop Streaming.
- `books_spark`: dataset do Pig tạo cho Spark/PySpark.
- `analytics/mapreduce/*`: output các job MapReduce.
- `analytics/spark/*`: output các job Spark.
- `quality/quality_report.json`: output báo cáo Data Quality.

### 9.3. HBase/Phoenix

- `bookbigdata:books_hbase`: bảng HBase lưu dữ liệu sách dạng Column-Family.
- `"bookbigdata"."books_hbase"`: Phoenix mapped View ánh xạ trực tiếp bảng HBase vật lý.
- `BOOKBIGDATA.BOOKS`: Phoenix View read-only dùng làm tên truy vấn thống nhất cho Web.
- HBase Thrift Server và HappyBase: lớp truy cập dùng cho thao tác CRUD.
- HBase Snapshot: các bản backup theo thời điểm của bảng `bookbigdata:books_hbase`.

## 10. Cấu trúc Web

Menu chính gồm:

- Quản lý sách.
- Truy vấn Phoenix SQL.
- Phân tích dữ liệu.
- Data Quality.
- Backup & Restore HBase.

## 11. Công nghệ sử dụng

- Python
- Flask
- Bootstrap
- Chart.js
- WSL Ubuntu
- MySQL
- Hadoop HDFS
- YARN
- Sqoop
- Pig
- Hive
- Drill
- MapReduce
- Spark/PySpark
- HBase
- Phoenix
- HappyBase
- HBase Thrift Server
- ZooKeeper

## 12. Phân công công việc

### 12.1. Công việc chung của toàn bộ thành viên

Mọi người đều tham gia cài đặt, cấu hình và kiểm thử môi trường WSL Ubuntu
single node gồm HDFS, YARN, Sqoop, Pig, Hive, Drill, Spark, HBase, Phoenix và
ZooKeeper.

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
| `<Tên thành viên>` | Crawl + ETL | Khảo sát Tiki và Fahasa; crawl bằng Scrapy; lưu raw JSON; chuẩn hóa schema; validate dữ liệu; xuất `books_clean.csv`. | `crawler_etl/config/`, `crawler_etl/scrapy_crawler/`, `crawler_etl/etl/`, `data/raw/`, `data/clean/` |
| `<Tên thành viên>` | Flask Web + Backup HBase | Xây dựng Web đọc, search, filter và phân trang qua Phoenix; thực hiện CRUD trực tiếp trên HBase bằng HappyBase; giao diện Bootstrap; Chart.js; trang truy vấn Phoenix SQL; đọc Analytics và Data Quality từ HDFS bằng WebHDFS; giao diện backup/restore HBase Snapshot. | `web/app.py`, `web/routes/`, `web/services/`, `web/templates/`, `web/static/`, `scripts/windows/run_web.bat` |
| `<Tên thành viên>` | MySQL + Hadoop nền + Pig/Hive/Drill | Thiết kế schema MySQL staging; import CSV; cấu hình HDFS, YARN, Sqoop; dùng Pig tạo dataset MapReduce/Spark; tạo Hive External Table; cấu hình Drill và viết SQL tạo báo cáo Data Quality. | `database/`, `hadoop/sqoop/`, `hadoop/pig/`, `hadoop/hive/`, `hadoop/drill/`, `scripts/ubuntu/run_sqoop.sh`, `scripts/ubuntu/run_pig.sh`, `scripts/ubuntu/run_drill.sh`, `docs/setup/setup_hadoop.md`, `docs/setup/setup_hive_pig_drill.md` |
| `<Tên thành viên>` | Phân tích 1: MapReduce | Viết 8 job Hadoop Streaming; thiết kế output chuẩn cho Web; chạy job trên dataset `books_mr`; lưu kết quả trên HDFS. | `hadoop/mapreduce/`, `scripts/ubuntu/run_mapreduce_all.sh` |
| `<Tên thành viên>` | Phân tích 2: Spark/PySpark + HBase/Phoenix/ZooKeeper | Viết PySpark phân tích nâng cao; tạo output trên HDFS; cài đặt và cấu hình HBase, Phoenix, ZooKeeper; thiết kế bảng `bookbigdata:books_hbase`; import dữ liệu sách vào HBase dạng chuỗi; tạo Phoenix View ánh xạ và bật HBase Thrift Server. | `hadoop/spark/`, `hadoop/hbase/`, `hadoop/phoenix/`, `scripts/ubuntu/run_spark.sh`, `scripts/ubuntu/run_hbase_phoenix.sh`, `docs/setup/setup_spark.md`, `docs/setup/setup_hbase_phoenix_zookeeper.md` |

### 12.3. Contract tích hợp giữa các module

Cần thống nhất và không tự ý thay đổi các contract sau:

Chi tiết schema output và các vị trí cần cập nhật khi output thay đổi xem tại
[`docs/output_contract.md`](docs/output_contract.md).

- Schema chung gồm 17 cột theo mục 6.
- MySQL chỉ là staging database, không dùng làm database chính của Web.
- HDFS landing nằm tại `/book_project/landing/books`.
- Pig tạo hai dataset chính: `books_mr` và `books_spark`.
- Output MapReduce dùng CSV có header; output Spark dùng JSON Lines.
- Đường dẫn HDFS bắt đầu từ `/book_project`.
- Flask hiển thị, tìm kiếm, lọc, phân trang và truy vấn sách thông qua Phoenix View `BOOKBIGDATA.BOOKS`.
- Flask thêm, cập nhật và xóa sách trực tiếp trên HBase thông qua HappyBase và HBase Thrift Server.
- Flask đọc Analytics và Data Quality từ HDFS bằng WebHDFS API.
- Backup/restore thực hiện trên HBase bằng HBase Snapshot.

## 13. Kết quả cuối cùng

Hệ thống hoàn chỉnh cho phép nhóm thu thập dữ liệu sách từ internet, chuẩn hóa
dữ liệu, lưu tạm vào MySQL trong WSL, đưa dữ liệu lên HDFS bằng Sqoop, tạo các
dataset phân tích bằng Pig, quản lý metadata bằng Hive, phân tích bằng
MapReduce và Spark/PySpark, kiểm tra Data Quality bằng Drill, lưu dữ liệu sách
phục vụ Web trong HBase và truy vấn đọc bằng Phoenix. Web Flask thực hiện CRUD
trực tiếp trên HBase bằng HappyBase, hiển thị Analytics/Data Quality từ HDFS
và hỗ trợ backup/restore HBase bằng Snapshot.
