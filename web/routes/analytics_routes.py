from __future__ import annotations

from flask import Blueprint, current_app, render_template, request

from services.chart_service import chart_payload, columns


analytics_blueprint = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_blueprint.get("")
def index():
    selected = request.args.get("dataset", "source_count")
    service = current_app.extensions["hdfs_service"]
    datasets = service.analytics_datasets()
    if selected not in datasets:
        selected = "source_count"
    error = None
    try:
        title, rows = (
            service.analytics_rows(selected)
            if current_app.config["WEB_DATA_MODE"] == "mock"
            else service.read_dataset(selected)
        )
    except Exception as caught:
        title, rows = datasets[selected][0], []
        error = f"Không thể đọc output HDFS: {caught}"
    groups = {"MapReduce": [], "Spark": []}
    for key, config in datasets.items():
        groups.setdefault(config[1], []).append((key, config[0]))
    return render_template(
        "analytics.html",
        datasets=datasets,
        groups=groups,
        selected=selected,
        selected_group=datasets[selected][1],
        title=title,
        rows=rows,
        columns=columns(rows),
        chart=chart_payload(rows, **service.analytics_chart_config(selected)),
        error=error,
    )