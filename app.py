from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import pandas as pd


load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Rainfall(db.Model):
    __tablename__ = 'rainfall_guage_a'
    datetimestamp = db.Column(db.DateTime, primary_key=True)
    rainfall = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Rainfall {self.datetimestamp}: {self.rainfall}>"
    
    
    
def import_excel():
    df = pd.read_excel("data/rainfall.xlsx", sheet_name="RG_A")
    df.columns = ["datetimestamp", "rainfall"]
    df["datetimestamp"] = pd.to_datetime(df["datetimestamp"])

    with app.app_context():
        engine = db.engine
        df.to_sql("rainfall_guage_a", engine, if_exists="replace", index=False)
        print("Imported Excel to Database")



def load_dataframe(start=None, end=None):

    query = Rainfall.query

    if start:
        query = query.filter(Rainfall.datetimestamp >= start)
    if end:
        query = query.filter(Rainfall.datetimestamp <= end)

    records = query.order_by(Rainfall.datetimestamp).all()

    df = pd.DataFrame([{
        "datetimestamp": r.datetimestamp,
        "rainfall": r.rainfall
    } for r in records])

    if df.empty:
        return df

    df["date"] = df["datetimestamp"].dt.date
    return df


@app.route('/rainfall-data')
def rainfall_data():
    data = Rainfall.query.all()
    df = pd.DataFrame([{'datetimestamp': r.datetimestamp, 'rainfall': r.rainfall} for r in data])

    # Aggregate by day
    df['date'] = df['datetimestamp'].dt.date
    daily = df.groupby('date')['rainfall'].sum().reset_index()

    labels = daily['date'].astype(str).tolist()
    values = daily['rainfall'].tolist()
    return jsonify({"labels": labels, "values": values})


@app.route('/')
def index():
    return 'Test'

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        import_rainfall_data()
    app.run(debug=True)