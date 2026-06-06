"""Flask entry point for Book Big Data Analytics System."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from routes.analytics_routes import analytics_blueprint
from routes.backup_routes import backup_blueprint
from routes.book_routes import book_blueprint
from routes.quality_routes import quality_blueprint
from services.backup_service import BackupService
from services.hdfs_service import HDFSService
from services.mysql_service import MySQLService


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def create_app() -> Flask:
    load_dotenv(PROJECT_ROOT / ".env")
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "development-key")

    mysql = MySQLService()
    app.extensions["mysql_service"] = mysql
    app.extensions["hdfs_service"] = HDFSService()
    app.extensions["backup_service"] = BackupService(mysql)

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
