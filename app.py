from flask import Flask, render_template, jsonify
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

@app.route("/rainfall-data-simple")
def rainfall_data_simple():
    rows = Rainfall.query.order_by(Rainfall.datetimestamp).all()
    if not rows:
        return jsonify({"labels": [], "values": []})
    
    df = pd.DataFrame([{"ts": r.datetimestamp, "rain": r.rainfall} for r in rows])
    df["date"] = df["ts"].dt.date
    daily = df.groupby("date")["rain"].sum().reset_index()

    labels = daily["date"].astype(str).tolist()
    values = daily["rain"].astype(float).tolist()

    return jsonify({
        "labels": labels,
        "values": values
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
