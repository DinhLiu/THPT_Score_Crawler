# Crawl_THPTQG

A small Python scraper that collects 2025 high school national exam scores from diemthi.vnexpress.net and stores them in a PostgreSQL database.

## What this project does

- Visits student detail pages on [diemthi.vnexpress.net](https://diemthi.vnexpress.net) for year 2025.
- Extracts scores for the following subjects: Toán, Ngữ văn, Vật lý, Hóa học, Sinh học, Lịch sử, Địa lý, GDCD, Ngoại ngữ.
- Inserts the scores into a PostgreSQL table named `scores`.

The main script is `main.py`.

## Requirements

- Python 3.10+ (the code was run with CPython 3.13 in the workspace but 3.10+ is recommended)
- PostgreSQL server
 - Python packages:
	 - requests_html
	 - psycopg2

It's recommended to run inside a virtual environment.

## Quick setup

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Prepare PostgreSQL:

	- Create a database (the script expects a database called `thptqg_2025` by default).
	- Create the `scores` table (example schema below).

Example SQL to create the `scores` table:

```sql
CREATE TABLE scores (
  id SERIAL PRIMARY KEY,
  math REAL,
  literature REAL,
  physics REAL,
  chemistry REAL,
  biology REAL,
  history REAL,
  geography REAL,
  civic_education REAL,
  foreign_language REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

4. Database credentials (recommended):

`main.py` now reads database connection parameters from environment variables. You can create a `.env` file in the project root (the project uses `python-dotenv` to load it) with the following example values:

```env
THPTQG_DB_NAME=thptqg_2025
THPTQG_DB_USER=postgres
THPTQG_DB_PASSWORD=12312312
THPTQG_DB_HOST=localhost
THPTQG_DB_PORT=5432
```

If no environment variables are present, sensible defaults are used (matching the previous hardcoded values). For production, set secure credentials in your environment and do not commit `.env` to source control.

## How to run

From the project root (with the venv active):

```powershell
python main.py
```

The script will:

- Delete all existing rows from the `scores` table at start (see `DELETE_QUERY`).
- Crawl student pages in the hardcoded province range (in the provided code the for-loop iterates `range(40, 42)`) and sequential student ids.
- Stop when `STOP_RANGE` consecutive IDs return no result (currently 5).

## Implementation notes

- The scraper uses `requests_html.HTMLSession` to fetch pages and parse HTML.
- Scores are normalized with `safe_float()` which returns `None` for missing/non-numeric values so they insert as SQL NULL.
- The script currently commits each insert immediately. For better performance you can batch inserts and commit in bulk.

## Troubleshooting

- If you get connection errors to PostgreSQL, verify the server is running and the credentials are correct.
- If the scraper doesn't find data, open the target URL in a browser to confirm the page layout hasn't changed. The scraper looks for `.o-detail-thisinh` and table rows inside `tbody`.
- For network issues consider adding retries, timeouts and a small delay between requests to avoid getting blocked.

## Security and ethics

- This scraper hits a public website. Respect the site's robots.txt and rate limits. Avoid aggressive or distributed scraping that may overload the target site.
- Do not commit production database credentials to source control. Switch to environment variables or a secrets manager.

## Next steps / improvements

1. Add `requirements.txt` with pinned versions.
2. Move DB credentials to environment variables and use a simple config loader.
3. Add exponential backoff + retry logic and rate limiting between requests.
4. Add logging instead of print statements.
5. Add unit tests for parsing logic and a small integration test that writes to a local test database.
6. Consider concurrent crawling (with careful rate limiting) to speed up collection.

## License

This project is provided as-is for educational purposes. Add a license file if you want to publish it.

---

Files of interest:

- `main.py` — main crawler and DB inserter.
