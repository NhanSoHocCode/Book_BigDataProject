"""Analytics dashboard routes backed by WebHDFS."""

from __future__ import annotations

from flask import Blueprint, current_app, render_template, request

from services.chart_service import chart_payload, columns
from services.hdfs_service import DATASETS


analytics_blueprint = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_blueprint.get("")
def index():
    selected = request.args.get("dataset", "source_count")
    error = None
    title = DATASETS.get(selected, ("Unknown dataset", "", ""))[0]
    rows = []
    try:
        title, rows = current_app.extensions["hdfs_service"].read_dataset(selected)
    except Exception as exception:
        error = str(exception)
    return render_template(
        "analytics.html",
        datasets=DATASETS,
        selected=selected,
        title=title,
        rows=rows,
        columns=columns(rows),
        chart=chart_payload(rows),
        error=error,
    )
