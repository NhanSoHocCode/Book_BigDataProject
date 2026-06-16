from __future__ import annotations

from typing import Any


def columns(rows: list[dict[str, Any]]) -> list[str]:
    found: list[str] = []
    for row in rows:
        for key in row:
            if key not in found:
                found.append(key)
    return found

def chart_payload(rows, label_key=None, value_key=None, chart_type="bar", title=""):
    if not rows:
        return None
    
    data_obj = rows[0] if isinstance(rows, list) and len(rows) > 0 else rows
    
    if isinstance(data_obj, dict) and ("QUALITY_CHECKS" in data_obj or "QUALITY_CHECKS".lower() in [k.lower() for k in data_obj.keys()]):
        qc_data = data_obj.get("QUALITY_CHECKS", {})
        missing_data = qc_data.get("missing_required", {})
        
        return {
            "labels": ["Hợp lệ (Valid)", "Bị loại (Rejected)", "Thiếu Book ID", "Thiếu Title"],
            "datasets": [{
                "label": "Số lượng dòng dữ liệu (Records)",
                "data": [
                    int(qc_data.get("valid_records", 0)),
                    int(qc_data.get("rejected_records", 0)),
                    int(missing_data.get("missing_book_id", 0)),
                    int(missing_data.get("missing_title", 0)),
                    int(missing_data.get("mising_source", 0))
                ],
                "backgroundColor": [
                    "rgba(40, 167, 69, 0.7)",   # Xanh lá cho dữ liệu sạch
                    "rgba(220, 53, 69, 0.7)",   # Đỏ cho dữ liệu lỗi bị loại
                    "rgba(255, 193, 7, 0.7)",   # Vàng cảnh báo
                    "rgba(255, 159, 64, 0.7)"   # Cam cảnh báo
                ],
                "borderWidth": 1
            }]
        }
        
    chart_type = chart_type if chart_type else "bar"
    
    def to_num(val):
        if val is None: return 0
        val_str = str(val).replace(",", "").strip()
        if not val_str or val_str.lower() in ["none", "null"]: return 0
        try:
            num = float(val_str)
            return int(num) if num.is_integer() else round(num, 2)
        except ValueError:
            return 0

    if rows and any(k in rows[0] for k in ["total_sold", "book_count", "avg_price", "avg_rating"]) and chart_type in ["grouped_bar", "stacked_bar", "line"]:
        if "source" in rows[0]:
            labels = [str(r.get("source", "")).upper() for r in rows]
        elif "main_category" in rows[0]:
            rows = rows[:10]
            labels = [str(r.get("main_category", "")) for r in rows]
        else:
            labels = [str(r.get(label_key, "")) for r in rows[:10]]
            rows = rows[:10]

        return {
            "type": "bar",
            "chart_style_meta": "spark_multi_axis",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "type": "bar",
                        "label": "Tổng lượng bán",
                        "data": [to_num(r.get("total_sold", 0)) for r in rows],
                        "backgroundColor": "rgba(54, 162, 235, 0.7)",
                        "yAxisID": "y_volume"
                    },
                    {
                        "type": "bar",
                        "label": "Số lượng đầu sách",
                        "data": [to_num(r.get("book_count", 0)) for r in rows],
                        "backgroundColor": "rgba(255, 159, 64, 0.7)",
                        "yAxisID": "y_right_count"
                    },
                    {
                        "type": "line",
                        "label": "Giá trung bình (VNĐ)",
                        "data": [to_num(r.get("avg_price", 0)) for r in rows],
                        "borderColor": "#4bc0c0",
                        "backgroundColor": "transparent",
                        "borderWidth": 3,
                        "yAxisID": "y_price",
                        "tension": 0.2
                    },
                    {
                        "type": "line",
                        "label": "Rating trung bình",
                        "data": [to_num(r.get("avg_rating", 0)) for r in rows],
                        "borderColor": "#e63946",
                        "backgroundColor": "transparent",
                        "borderWidth": 3,
                        "yAxisID": "y_rating",
                        "tension": 0.2
                    }
                ]
            }
        }
    
    if chart_type == "bubble":
        plot_rows = rows[:15]
        labels = [str(r.get(label_key, "")) for r in plot_rows]
        bubble_data = [{"x": idx + 1, "y": to_num(r.get(value_key, 0)), "r": 10} for idx, r in enumerate(plot_rows)]
        return {
            "type": "bubble",
            "chart_style_meta": "mr_bubble",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": title,
                    "data": bubble_data,
                    "backgroundColor": "rgba(153, 102, 255, 0.6)",
                    "borderColor": "rgba(153, 102, 255, 1)"
                }]
            }
        }

    if chart_type == "scatter":
        plot_rows = rows[:15]
        labels = [str(r.get("title", "")) for r in plot_rows]
        scatter_data = [{"x": idx + 1, "y": to_num(r.get(value_key, 0))} for idx, r in enumerate(plot_rows)]
        return {
            "type": "scatter",
            "chart_style_meta": "mr_scatter",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": title,
                    "data": scatter_data,
                    "backgroundColor": "#ff6384",
                    "pointRadius": 8
                }]
            }
        }

    plot_rows = rows[:10]
    labels = [str(r.get(label_key, "")) for r in plot_rows]
    data_values = [to_num(r.get(value_key, 0)) for r in plot_rows]
    
    colors = ["#36a2eb", "#ff6384", "#4bc0c0", "#ff9f40", "#9966ff", "#ffcd56", "#c9cbcf", "#457b9d", "#e63946", "#a8dadc"]
    
    is_horizontal = (chart_type == "horizontalBar")
    
    return {
        "type": "bar" if is_horizontal else chart_type,
        "chart_style_meta": "horizontal" if is_horizontal else chart_type,
        "data": {
            "labels": labels,
            "datasets": [{
                "label": title,
                "data": data_values,
                "backgroundColor": colors if chart_type in ["pie", "doughnut", "polarArea", "radar"] else colors[0],
                "borderColor": colors if chart_type in ["pie", "doughnut", "polarArea", "radar"] else colors[0],
                "borderWidth": 1
            }]
        }
    }