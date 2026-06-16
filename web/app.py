from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from routes.analytics_routes import analytics_blueprint
from routes.backup_routes import backup_blueprint
from routes.book_routes import book_blueprint
from routes.dashboard_routes import dashboard_blueprint
from routes.quality_routes import quality_blueprint
from services.backup_service import HBaseSnapshotService
from services.happybase_service import HappyBaseBookService
from services.hdfs_service import HDFSService
from services.mock_service import MockDataService
from services.phoenix_service import PhoenixBookService


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def create_app() -> Flask:
    load_dotenv(PROJECT_ROOT / ".env")
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "development-key")
    data_mode = os.getenv("WEB_DATA_MODE", "mock").strip().casefold()
    if data_mode not in {"mock", "live"}:
        raise ValueError("WEB_DATA_MODE chỉ được là mock hoặc live.")
    app.config["WEB_DATA_MODE"] = data_mode
    app.config["PHOENIX_BOOKS_VIEW"] = os.getenv(
        "PHOENIX_BOOKS_VIEW",
        "bookbigdata.books_hbase",
    )
    app.config["HBASE_TABLE"] = os.getenv(
        "HBASE_TABLE",
        "bookbigdata:books_hbase",
    )
    app.config["HDFS_QUALITY_REPORT"] = os.getenv(
        "HDFS_QUALITY_REPORT",
        "/book_project/quality/quality_report.json",
    )

    if data_mode == "mock":
        mock_service = MockDataService()
        app.extensions["book_query_service"] = mock_service
        app.extensions["book_crud_service"] = mock_service
        app.extensions["hdfs_service"] = mock_service
        app.extensions["backup_service"] = mock_service
    else:
        app.extensions["book_query_service"] = PhoenixBookService()
        app.extensions["book_crud_service"] = HappyBaseBookService()
        app.extensions["hdfs_service"] = HDFSService()
        app.extensions["backup_service"] = HBaseSnapshotService()

    @app.context_processor
    def web_data_context() -> dict[str, object]:
        return {
            "data_mode": app.config["WEB_DATA_MODE"],
            "is_mock": app.config["WEB_DATA_MODE"] == "mock",
            "phoenix_books_relation": app.config["PHOENIX_BOOKS_VIEW"],
            "hbase_table": app.config["HBASE_TABLE"],
            "quality_report_path": app.config["HDFS_QUALITY_REPORT"],
        }

    app.register_blueprint(dashboard_blueprint)
    app.register_blueprint(book_blueprint)
    app.register_blueprint(analytics_blueprint)
    app.register_blueprint(quality_blueprint)
    app.register_blueprint(backup_blueprint)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
