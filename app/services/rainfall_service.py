from models import Rainfall
from sqlalchemy.sql import text


def get_aggregated_rainfall(mode: str):
    """
    native Postgres aggregation.
    """

    from app import db

    if mode == "day":
        bucket = "date(datetimestamp)"
        fmt = "YYYY-MM-DD"
    elif mode == "month":
        bucket = "date_trunc('month', datetimestamp)"
        fmt = "YYYY-MM"
    else:  # week
        bucket = "date_trunc('week', datetimestamp)"
        fmt = "YYYY-MM-DD"

    sql = text(f"""
        SELECT 
            to_char({bucket}, '{fmt}') AS label,
            SUM(rainfall) AS value
        FROM rainfall_guage_a
        GROUP BY label
        ORDER BY label;
    """)

    rows = db.session.execute(sql).fetchall()
    labels = [r.label for r in rows]
    values = [float(r.value) for r in rows]

    return labels, values


def get_rainfall_stats():
    """
    Compute stats using SQL
    """

    from app import db

    sql = text("""
        WITH daily AS (
            SELECT 
                date(datetimestamp) AS d,
                SUM(rainfall) AS total
            FROM rainfall_guage_a
            GROUP BY d
        )
        SELECT
            (SELECT SUM(total) FROM daily) AS total_rainfall,
            (SELECT total FROM daily ORDER BY total DESC LIMIT 1) AS max_daily,
            (SELECT d FROM daily ORDER BY total DESC LIMIT 1) AS max_daily_date,
            (SELECT AVG(total) FROM daily) AS avg_daily,
            (SELECT COUNT(*) FROM daily WHERE total > 0.2) AS rainy_days,
            (SELECT COUNT(*) FROM daily WHERE total <= 0.2) AS dry_days;
    """)

    row = db.session.execute(sql).mappings().first()

    return {
        "total_rainfall": float(row["total_rainfall"]),
        "max_daily": float(row["max_daily"]),
        "max_daily_date": str(row["max_daily_date"]),
        "avg_daily": float(row["avg_daily"]),
        "rainy_days": int(row["rainy_days"]),
        "dry_days": int(row["dry_days"]),
    }
