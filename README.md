# StantecDataVisualization

Quick start (recommended)
1. Clone
   git clone <repo-url> StantecDataVisualization
   cd StantecDataVisualization

2. Create and activate a virtual environment
   python -m venv env
   source env/bin/activate

3. Install dependencies
   pip install flask sqlalchemy psycopg2-binary pandas openpyxl python-dotenv chart.js

   (If you prefer SQLite only, psycopg2-binary is optional.)

4. Configure the database
   - By default the app will fall back to a local SQLite file if no DATABASE_URL is set.
   - To use Postgres, create a DATABASE_URL env var (example in .env):
     DATABASE_URL=postgresql://user:password@localhost:5432/rainfall_db

   Create a `.env` in the project root if using Postgres:
   echo "DATABASE_URL=postgresql://user:pass@localhost:5432/rainfall_db" > .env

5. Import rainfall data from Excel (if you have the file)
   - Place your Excel at `app/data/rainfall.xlsx` (sheet name `RG_A`)
   - Or run:
     python app/scripts/import_rainfall.py --file app/data/rainfall.xlsx --sheet RG_A

   The script will convert the timestamp column to datetime and write to the DB table `rainfall_guage_a`.

Run the app
- From project root (recommended):
  python -m app.app

- Or using flask CLI:
  export FLASK_APP=app.app
  flask run

Open in browser
- http://127.0.0.1:5000/

What you can do in the UI
- Toggle aggregation: Day / Week (default) / Month
- Apply date range using the From / To pickers (YYYY-MM-DD). The API accepts `start` and `end` query params.
- Click a week/month point on the chart to drill down to day-level for that period.

Testing (optional)
- If you add pytest tests, run:
  pip install pytest
  pytest -q

Troubleshooting
- 403 responses on fetch:
  - Check Network tab for exact URL and server logs.
  - Ensure you're calling the correct host/port and not blocked by CORS or auth.
- 500 errors when filtering by date:
  - Ensure the service code uses CAST(:param AS date) (not `:param::date`) so SQLAlchemy binds correctly.
  - Check server console for full traceback.
- Circular import errors:
  - The codebase lazy-imports the database (db) inside service functions. If you re-introduce top-level imports, move them into function scope.
- Import failures:
  - The import script will print errors. Re-run with --file pointing to the correct Excel and ensure sheet name is RG_A.
- If using Postgres, ensure the user/schema has permission to CREATE/REPLACE the `rainfall_guage_a` table.

Code structure
- app/ — application package
  - app.py — Flask application factory / entry
  - models.py — SQLAlchemy models
  - routes/ — Flask blueprints (api, pages)
  - services/ — SQL-based aggregation and stats
  - scripts/import_rainfall.py — Excel → DB import
  - templates/dashboard.html — frontend UI