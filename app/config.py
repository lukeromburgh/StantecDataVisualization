import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/rainfall")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
