import pandas as pd
from app import create_app, db
from models import Rainfall

def import_excel():
    df = pd.read_excel("data/rainfall.xlsx", sheet_name="RG_A")
    df.columns = ["datetimestamp", "rainfall"]
    df["datetimestamp"] = pd.to_datetime(df["datetimestamp"])

    app = create_app()
    with app.app_context():
        engine = db.get_engine()

        # Write directly into Postgres table
        df.to_sql("rainfall_guage_a",
                  engine,
                  if_exists="replace",
                  index=False)

        print("Excel → Postgres import completed.")


if __name__ == "__main__":
    import_excel()
