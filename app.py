from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd


load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(DATABASE_URL)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def get_rainfall_data():
    rainfall = pd.read_excel("data/rainfall.xlsx", sheet_name="RG_A")
    rainfall.head(5)
    rainfall.to_sql("rainfall_guage_a")

@app.route('/')
def index():
    return 'Test'

if __name__ == "__main__":
    app.run(debug=True)