# Cài đặt môi trường phát triển trên Windows

## Công cụ cần thiết

- MySQL Server 8.x
- MySQL Client hoặc MySQL Workbench

## Môi trường Python

Chạy các lệnh sau tại thư mục gốc của dự án:

```bat
pip install -r requirements.txt
copy .env.example .env
```

Cập nhật file `.env` với tài khoản MySQL local và URL WebHDFS của NameNode
Ubuntu.

## Luồng chạy local

```bat
scripts\windows\run_crawl_etl.bat
scripts\windows\import_mysql.bat
scripts\windows\run_web.bat
```

Mở `http://127.0.0.1:5000` trên trình duyệt.

Trang Analytics và Data Quality yêu cầu kết nối được tới NameNode Ubuntu đã
bật WebHDFS.
