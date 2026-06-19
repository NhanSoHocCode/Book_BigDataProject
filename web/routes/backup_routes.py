from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for


backup_blueprint = Blueprint("backup", __name__, url_prefix="/backup")


def service():
    return current_app.extensions["backup_service"]


@backup_blueprint.get("")
def index():
    error = None
    try:
        snapshots = service().list_snapshots()
    except Exception as caught:
        snapshots = []
        error = f"Không thể đọc danh sách HBase Snapshot: {caught}"
    return render_template("backup.html", snapshots=snapshots, error=error)


@backup_blueprint.post("/hbase")
def backup_hbase():
    try:
        snapshot = service().create_snapshot()
        flash(f"Đã tạo HBase Snapshot: {snapshot}", "success")
    except Exception as error:
        flash(f"Tạo HBase Snapshot thất bại: {error}", "danger")
    return redirect(url_for("backup.index"))


@backup_blueprint.post("/hbase/restore")
def restore_hbase():
    try:
        snapshot = service().restore_snapshot(request.form.get("snapshot", ""))
        flash(f"Đã restore HBase Snapshot: {snapshot}", "success")
    except Exception as error:
        flash(f"Restore HBase Snapshot thất bại: {error}", "danger")
    return redirect(url_for("backup.index"))


@backup_blueprint.post("/hbase/delete")
def delete_hbase_snapshot():
    try:
        snapshot = service().delete_snapshot(request.form.get("snapshot", ""))
        flash(f"Đã xóa HBase Snapshot: {snapshot}", "success")
    except Exception as error:
        flash(f"Xóa HBase Snapshot thất bại: {error}", "danger")
    return redirect(url_for("backup.index"))