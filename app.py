from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or "sqlite:///data/rainfall.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Rainfall(db.Model):
    __tablename__ = 'rainfall_guage_a'
    datetimestamp = db.Column(db.DateTime, primary_key=True)
    rainfall = db.Column(db.Float, nullable=False)

def import_excel():
    df = pd.read_excel("data/rainfall.xlsx", sheet_name="RG_A")
    df.columns = ["datetimestamp", "rainfall"]
    df["datetimestamp"] = pd.to_datetime(df["datetimestamp"])

    with app.app_context():
        engine = db.engine
        df.to_sql("rainfall_guage_a", engine, if_exists="replace", index=False)
        print("Imported Excel to Database")

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/rainfall-data")
def rainfall_data():
    mode = request.args.get("mode", "week").lower()  # default to week
    rows = Rainfall.query.order_by(Rainfall.datetimestamp).all()
    if not rows:
        return jsonify({"labels": [], "values": [], "mode": mode})

    df = pd.DataFrame([{"ts": r.datetimestamp, "rain": r.rainfall} for r in rows])
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.set_index("ts")

    if mode == "day":
        res = df["rain"].resample("D").sum()
        labels = res.index.strftime("%Y-%m-%d").tolist()
    elif mode == "month":
        res = df["rain"].resample("MS", label="left").sum()
        labels = res.index.strftime("%Y-%m").tolist()
    else:  # default: week
        res = df["rain"].resample("W-MON", label="left", closed="left").sum()
        labels = res.index.strftime("%Y-%m-%d").tolist()

    values = res.fillna(0).astype(float).tolist()

    return jsonify({
        "labels": labels,
        "values": values,
        "mode": mode
    })

@app.route("/rainfall-stats")
def rainfall_stats():
    rows = Rainfall.query.order_by(Rainfall.datetimestamp).all()
    if not rows:
        return jsonify({
            "total_rainfall": 0,
            "max_daily": 0,
            "max_daily_date": None,
            "avg_daily": 0,
            "rainy_days": 0,
            "dry_days": 0
        })

    df = pd.DataFrame([{"ts": r.datetimestamp, "rain": r.rainfall} for r in rows])
    df["date"] = df["ts"].dt.date
    daily = df.groupby("date")["rain"].sum().reset_index()

    total_rainfall = float(daily["rain"].sum())

    max_row = daily.loc[daily["rain"].idxmax()]
    max_daily = float(max_row["rain"])
    max_daily_date = str(max_row["date"])

    avg_daily = float(daily["rain"].mean())

    rainy_days = int((daily["rain"] > 0.2).sum())
    dry_days = int((daily["rain"] <= 0.2).sum())

    return jsonify({
        "total_rainfall": total_rainfall,
        "max_daily": max_daily,
        "max_daily_date": max_daily_date,
        "avg_daily": avg_daily,
        "rainy_days": rainy_days,
        "dry_days": dry_days
    })


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

