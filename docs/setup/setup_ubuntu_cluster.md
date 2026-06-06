# Cài đặt Ubuntu Cluster

## Các node

Sử dụng ít nhất một Ubuntu NameNode và một DataNode. Với mục đích demo trên
lớp, có thể chạy toàn bộ dịch vụ trên một máy ảo.

## Các package cần thiết

```bash
sudo apt update
sudo apt install -y openssh-server openssh-client rsync python3 curl mysql-client
```

Cài Java `11` để dùng cùng baseline Hadoop `3.3.6` của dự án:

```bash
sudo apt install -y openjdk-11-jdk
java -version
```

Cài Hadoop, Sqoop, Pig, Hive, Spark, Drill, HBase, Phoenix và ZooKeeper trong
thư mục `/opt`, sau đó thêm các thư mục `bin` tương ứng vào biến `PATH`. Dùng
đúng bộ phiên bản đã chốt tại mục `2.1` trong `README.md`.

Không chọn phiên bản mới nhất của từng công cụ một cách độc lập. Cả nhóm cần
chốt và kiểm thử một bộ phiên bản tương thích. Sqoop đã ngừng phát triển và
phải được tải từ Apache Attic Archive để phục vụ đồ án học tập này.

## Biến môi trường

Cấu hình tối thiểu:

```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=/opt/hadoop
export HDFS_PROJECT_ROOT=/book_project
export MYSQL_HOST=<mysql-host>
export MYSQL_PORT=3306
export MYSQL_DATABASE=book_big_data
export MYSQL_USER=<mysql-user>
export MYSQL_PASSWORD=<mysql-password>
```

Sao chép MySQL Connector/J vào thư mục `lib` của Sqoop.

## Thứ tự chạy pipeline

Chạy tại thư mục gốc của dự án:

```bash
bash scripts/ubuntu/run_sqoop.sh
bash scripts/ubuntu/run_pig.sh
bash scripts/ubuntu/run_mapreduce_all.sh
bash scripts/ubuntu/run_spark.sh
bash scripts/ubuntu/run_drill.sh
```

Demo NoSQL tùy chọn:

```bash
bash scripts/ubuntu/run_hbase_phoenix.sh
```
