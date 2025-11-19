from app import db
from sqlalchemy import DateTime, Float

class Rainfall(db.Model):
    __tablename__ = "rainfall_guage_a"

    datetimestamp = db.Column(DateTime, primary_key=True, index=True)
    rainfall = db.Column(Float, nullable=False)
