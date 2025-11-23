from sqlalchemy.sql import text
import logging
import re

logger = logging.getLogger(__name__)

def _build_range_clause(start, end):
    """
    Build SQL WHERE clause and params.
    - If start/end are date-only strings (YYYY-MM-DD) use date(...) BETWEEN ... AND ...
    - Otherwise use inclusive timestamp comparisons.
    Returns tuple: (where_sql, params)
    """
    clauses = []
    params = {}
    is_date_only = lambda s: bool(re.match(r"^\d{4}-\d{2}-\d{2}$", s)) if s else False

    if start and end and is_date_only(start) and is_date_only(end):
        # user supplied date range e.g. 2018-01-21 to 2018-01-21 -> include that full day
        params["start"] = start
        params["end"] = end
        # use CAST(:param AS date) so SQLAlchemy binds correctly
        return "WHERE date(datetimestamp) BETWEEN CAST(:start AS date) AND CAST(:end AS date)", params

    if start:
        # use CAST for timestamp binding
        clauses.append("datetimestamp >= CAST(:start AS timestamp)")
        params["start"] = start
    if end:
        # make end inclusive and use CAST
        clauses.append("datetimestamp <= CAST(:end AS timestamp)")
        params["end"] = end

    if clauses:
        return "WHERE " + " AND ".join(clauses), params
    return "", params

# ...existing code...
def get_aggregated_rainfall(mode: str, start: str = None, end: str = None):
    """
    native Postgres aggregation with optional start/end (ISO date strings).
    Returns (labels, values)
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

    where_clause, params = _build_range_clause(start, end)

    sql = text(f"""
        SELECT 
            to_char({bucket}, '{fmt}') AS label,
            SUM(rainfall) AS value
        FROM rainfall_guage_a
        {where_clause}
        GROUP BY label
        ORDER BY label;
    """)

    try:
        rows = db.session.execute(sql, params).fetchall()
    except Exception:
        logger.exception("DB error during get_aggregated_rainfall")
        return [], []

    labels = [r.label for r in rows]
    values = [float(r.value) for r in rows]

    return labels, values

# ...existing code...
def get_rainfall_stats(start: str = None, end: str = None):
    """
    Compute stats using SQL with optional date range.
    """
    from app import db

    where_clause, params = _build_range_clause(start, end)

    sql = text(f"""
        WITH daily AS (
            SELECT 
                date(datetimestamp) AS d,
                SUM(rainfall) AS total
            FROM rainfall_guage_a
            {where_clause}
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

    try:
        row = db.session.execute(sql, params).mappings().first()
    except Exception:
        logger.exception("DB error during get_rainfall_stats")
        return {
            "total_rainfall": 0.0,
            "max_daily": 0.0,
            "max_daily_date": None,
            "avg_daily": 0.0,
            "rainy_days": 0,
            "dry_days": 0,
        }

    return {
        "total_rainfall": float(row["total_rainfall"] or 0.0),
        "max_daily": float(row["max_daily"] or 0.0),
        "max_daily_date": str(row["max_daily_date"]) if row["max_daily_date"] is not None else None,
        "avg_daily": float(row["avg_daily"] or 0.0),
        "rainy_days": int(row["rainy_days"] or 0),
        "dry_days": int(row["dry_days"] or 0),
    }
