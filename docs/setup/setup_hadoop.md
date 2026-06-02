# Cài đặt Hadoop và WebHDFS

## Các dịch vụ chính

Cấu hình HDFS và YARN theo bản phân phối Hadoop đã chọn. Khởi động và kiểm tra
các dịch vụ:

```bash
start-dfs.sh
start-yarn.sh
jps
hdfs dfs -mkdir -p /book_project
hdfs dfs -ls /
```

## Bật WebHDFS

Thêm property sau vào file `hdfs-site.xml` trên NameNode:

```xml
<property>
  <name>dfs.webhdfs.enabled</name>
  <value>true</value>
</property>
```

Khởi động lại HDFS và kiểm tra REST API:

```bash
curl "http://localhost:9870/webhdfs/v1/book_project?op=LISTSTATUS&user.name=hdfs"
```

Cấu hình `HDFS_NAMENODE_URL`, `HDFS_USER` và `HDFS_PROJECT_ROOT` trong file
`.env` của Flask.

## Hadoop Streaming

Xác định đường dẫn streaming JAR và export trước khi chạy MapReduce:

```bash
export STREAMING_JAR="$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-<version>.jar"
bash scripts/ubuntu/run_mapreduce_all.sh
```
