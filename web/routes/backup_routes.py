"""Backup and restore routes."""

from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for


backup_blueprint = Blueprint("backup", __name__, url_prefix="/backup")


def service():
    return current_app.extensions["backup_service"]


@backup_blueprint.get("")
def index():
    logs = current_app.extensions["mysql_service"].list_backup_logs()
    return render_template("backup.html", logs=logs)


@backup_blueprint.post("/mysql")
def backup_mysql():
    try:
        path = service().backup_mysql()
        flash(f"MySQL backup created: {path}", "success")
    except Exception as error:
        flash(f"MySQL backup failed: {error}", "danger")
    return redirect(url_for("backup.index"))


@backup_blueprint.post("/mysql/restore")
def restore_mysql():
    try:
        path = service().restore_mysql(request.form.get("backup_path", ""))
        flash(f"MySQL restored from: {path}", "success")
    except Exception as error:
        flash(f"MySQL restore failed: {error}", "danger")
    return redirect(url_for("backup.index"))


@backup_blueprint.post("/hdfs")
def backup_hdfs():
    try:
        path = service().backup_hdfs(request.form.get("scope", "all"))
        flash(f"HDFS backup created: {path}", "success")
    except Exception as error:
        flash(f"HDFS backup failed: {error}", "danger")
    return redirect(url_for("backup.index"))


@backup_blueprint.post("/hdfs/restore")
def restore_hdfs():
    try:
        path = service().restore_hdfs(
            request.form.get("snapshot", ""),
            request.form.get("scope", ""),
        )
        flash(f"HDFS restored from: {path}", "success")
    except Exception as error:
        flash(f"HDFS restore failed: {error}", "danger")
    return redirect(url_for("backup.index"))
