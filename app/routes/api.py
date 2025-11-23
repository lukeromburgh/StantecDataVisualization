from flask import Blueprint, jsonify, request
from ..services.rainfall_service import get_aggregated_rainfall, get_rainfall_stats

api_bp = Blueprint("api", __name__)


@api_bp.route("/rainfall-data")
def rainfall_data():
    mode = request.args.get("mode", "week").lower()
    start = request.args.get("start")
    end = request.args.get("end")
    try:
        labels, values = get_aggregated_rainfall(mode, start=start, end=end)
        return jsonify({"labels": labels, "values": values, "mode": mode})
    except Exception as e:
        # non-fatal: return empty payload and 500
        return jsonify({"labels": [], "values": [], "mode": mode, "error": str(e)}), 500


@api_bp.route("/rainfall-stats")
def rainfall_stats():
    start = request.args.get("start")
    end = request.args.get("end")
    try:
        stats = get_rainfall_stats(start=start, end=end)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
