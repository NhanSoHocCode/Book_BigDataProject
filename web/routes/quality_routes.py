"""Data quality report route backed by WebHDFS."""

from __future__ import annotations

from flask import Blueprint, current_app, render_template

from services.chart_service import chart_payload, columns


quality_blueprint = Blueprint("quality", __name__, url_prefix="/quality")


@quality_blueprint.get("")
def index():
    rows = []
    error = None
    try:
        rows = current_app.extensions["hdfs_service"].read_quality_report()
    except Exception as exception:
        error = str(exception)
    return render_template(
        "data_quality.html",
        rows=rows,
        columns=columns(rows),
        chart=chart_payload(rows),
        error=error,
    )
