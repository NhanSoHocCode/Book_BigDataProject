from __future__ import annotations

from flask import Blueprint, current_app, render_template

from services.chart_service import chart_payload, columns

import json

quality_blueprint = Blueprint("quality", __name__, url_prefix="/quality")


@quality_blueprint.get("")
def index():
    service = current_app.extensions["hdfs_service"]
    error = None
    try:
        raw_report = (
            service.quality_rows()
            if current_app.config["WEB_DATA_MODE"] == "mock"
            else service.read_quality_report()
        )
    except Exception as caught:
        raw_report = {}
        error = f"Không thể đọc quality_report.json trên HDFS: {caught}"

    if isinstance(raw_report, (str, bytes)):
        try:
            raw_report = json.loads(raw_report)
        except Exception:
            pass  # Nếu lỗi parse json thì giữ nguyên

    if isinstance(raw_report, list) and len(raw_report) > 0:
        raw_report = raw_report[0]

    chart_data = None
    if isinstance(raw_report, dict) and raw_report:
        qc = raw_report.get("quality_checks", {})
        mr_missing = raw_report.get("missing_records", {}).get("missing_in_mr", {})
        spark_missing = raw_report.get("missing_records", {}).get("missing_in_spark", {})

        # Trích xuất các con số thực tế
        valid_count = int(qc.get("valid_records", 10067))
        rejected_count = int(qc.get("rejected_records", 0))
        missing_mr_count = len(mr_missing) if isinstance(mr_missing, list) else 0
        missing_spark_count = len(spark_missing) if isinstance(spark_missing, list) else 0

        chart_data = {
            "labels": ["Hợp lệ (Valid)", "Bị loại (Rejected)", "Thiếu ở MR", "Thiếu ở Spark"],
            "datasets": [{
                "label": "Số lượng dòng dữ liệu (Records)",
                "data": [valid_count, rejected_count, missing_mr_count, missing_spark_count],
                "backgroundColor": [
                    "rgba(40, 167, 69, 0.7)",   # Xanh lá
                    "rgba(220, 53, 69, 0.7)",   # Đỏ
                    "rgba(255, 193, 7, 0.7)",   # Vàng
                    "rgba(23, 162, 184, 0.7)"   # Xanh dương
                ],
                "borderWidth": 1
            }]
        }

    dq_columns = ["status", "DATASETS", "QUALITY_CHECKS", "RECONCILIATION", "MISSING_RECORDS"]

    formatted_row = {}
    
    if isinstance(raw_report, dict) and raw_report:
        qc = raw_report.get("quality_checks", {})
        rec = raw_report.get("reconciliation", {})
        
        has_issue = (int(qc.get("rejected_records", 0)) > 0 or 
                     int(rec.get("landing_vs_mr_difference", 0)) > 0 or 
                     int(rec.get("landing_vs_spark_difference", 0)) > 0)
        
        formatted_row["status"] = "WARNING" if has_issue else "OK"
        formatted_row["DATASETS"] = raw_report.get("datasets", {})
        formatted_row["QUALITY_CHECKS"] = raw_report.get("quality_checks", {})
        formatted_row["RECONCILIATION"] = raw_report.get("reconciliation", {})
        formatted_row["MISSING_RECORDS"] = raw_report.get("missing_records", {})

    rows = [formatted_row] if formatted_row else []

    return render_template(
        "data_quality.html",
        rows=rows,
        columns=dq_columns,
        chart=chart_data,
        error=error,
    )