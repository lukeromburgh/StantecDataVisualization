from flask import Blueprint, jsonify, request
from services.rainfall_service import get_aggregated_rainfall, get_rainfall_stats

api_bp = Blueprint("api", __name__)


@api_bp.route("/rainfall-data")
def rainfall_data():
    mode = request.args.get("mode", "week").lower()
    labels, values = get_aggregated_rainfall(mode)

    return jsonify({
        "labels": labels,
        "values": values,
        "mode": mode
    })


@api_bp.route("/rainfall-stats")
def rainfall_stats_route():
    return jsonify(get_rainfall_stats())
