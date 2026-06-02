# Cài đặt HBase, Phoenix và ZooKeeper

Lớp này minh họa tích hợp NoSQL và không bắt buộc đối với dashboard Flask.

## Các dịch vụ

Khởi động ZooKeeper và HBase, sau đó kiểm tra:

```bash
start-hbase.sh
jps
```

Các Java process dự kiến gồm `HMaster`, `HRegionServer` và `QuorumPeerMain`
khi ZooKeeper chạy riêng.

## Tạo bảng và truy vấn bằng Phoenix

Cấu hình địa chỉ ZooKeeper cho Phoenix nếu cần:

```bash
export PHOENIX_ZK=localhost:2181
export PHOENIX_SQLLINE=/opt/phoenix/bin/sqlline.py
bash scripts/ubuntu/run_hbase_phoenix.sh
```

Script tạo bảng HBase `books` và chạy file
`hadoop/phoenix/phoenix_queries.sql`.
