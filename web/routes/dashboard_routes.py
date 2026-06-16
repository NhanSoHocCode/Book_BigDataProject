from __future__ import annotations

from flask import Blueprint, current_app, render_template


dashboard_blueprint = Blueprint("dashboard", __name__)


@dashboard_blueprint.get("/")
@dashboard_blueprint.get("/dashboard")
def dashboard():
    if current_app.config["WEB_DATA_MODE"] == "mock":
        data = current_app.extensions["book_query_service"].dashboard()
    else:
        book_service = current_app.extensions["book_query_service"]
        crud_service = current_app.extensions["book_crud_service"]
        hdfs_service = current_app.extensions["hdfs_service"]
        backup_service = current_app.extensions["backup_service"]
        errors: list[str] = []
        try:
            data = book_service.dashboard_metrics()
        except Exception as error:
            data = {
                "total_books": "Không khả dụng",
                "tiki_books": "Không khả dụng",
                "fahasa_books": "Không khả dụng",
                "categories": "Không khả dụng",
                "authors": "Không khả dụng",
            }
            errors.append(f"Phoenix: {error}")
        try:
            snapshots = backup_service.list_snapshots()
            data["last_backup"] = snapshots[0]["created_at"] if snapshots else "Chưa có"
        except Exception as error:
            data["last_backup"] = "Không khả dụng"
            errors.append(f"HBase Snapshot: {error}")

        phoenix_ok, phoenix_message = book_service.healthcheck()
        happybase_ok, happybase_message = crud_service.healthcheck()
        hdfs_ok, hdfs_message = hdfs_service.healthcheck()
        analytics_ok = hdfs_service.path_exists("/analytics")
        quality_ok = hdfs_service.path_exists(hdfs_service.quality_report)
        data["statuses"] = [
            {
                "name": "Phoenix JDBC",
                "status": phoenix_message if phoenix_ok else "Mất kết nối",
                "variant": "success" if phoenix_ok else "danger",
            },
            {
                "name": "HBase Thrift / HappyBase",
                "status": happybase_message if happybase_ok else "Mất kết nối",
                "variant": "success" if happybase_ok else "danger",
            },
            {
                "name": "WebHDFS",
                "status": hdfs_message if hdfs_ok else "Mất kết nối",
                "variant": "success" if hdfs_ok else "danger",
            },
            {
                "name": "Analytics output",
                "status": "Sẵn sàng" if analytics_ok else "Chưa có",
                "variant": "success" if analytics_ok else "warning",
            },
            {
                "name": "Data Quality report",
                "status": "Sẵn sàng" if quality_ok else "Chưa có",
                "variant": "success" if quality_ok else "warning",
            },
        ]
        data["errors"] = errors
    return render_template(
        "dashboard.html",
        dashboard=data,
    )