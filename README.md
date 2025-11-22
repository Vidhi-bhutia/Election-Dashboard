# Indian General Election Dashboard

A Streamlit frontend + FastAPI backend that provides interactive visualizations and analytics for Lok Sabha election data (1991–2019) powered by a cleaned LokDhaba CSV dataset.

## Quick links
- Frontend: [app.py](app.py) — Streamlit UI and renderers (e.g. [`app.get_analytics`](app.py), [`app.get_filters`](app.py))
- Backend API: [backend/app/main.py](backend/app/main.py) — FastAPI endpoints (e.g. [`backend.app.main.get_filters`](backend/app/main.py), [`backend.app.main.party_seat_share`](backend/app/main.py))
- SQL queries and data access: [backend/app/queries.py](backend/app/queries.py) (e.g. [`backend.app.queries.get_filters`](backend/app/queries.py), [`backend.app.queries.vote_share_trend`](backend/app/queries.py))
- Data loader: [backend/scripts/load_data.py](backend/scripts/load_data.py) (functions: [`backend.scripts.load_data.load_database`](backend/scripts/load_data.py))
- Original CSV: [All_States_GE.csv](All_States_GE.csv)
- Database config: [backend/app/config.py](backend/app/config.py) and DB access: [backend/app/database.py](backend/app/database.py)
- Schemas: [backend/app/schemas.py](backend/app/schemas.py)
- Requirements: [requirements.txt](requirements.txt) and [backend/requirements.txt](backend/requirements.txt)
- Persisted DB location: [data/](data/) (default DB: `data/elections.db`)

## Project overview
- The CSV [All_States_GE.csv](All_States_GE.csv) is cleaned and transformed by [`backend/scripts/load_data.py`](backend/scripts/load_data.py) into an SQLite DB (`data/elections.db`).
- The backend exposes endpoints for filters, aggregations and analytics (see [`backend/app/main.py`](backend/app/main.py)). Core SQL logic lives in [`backend/app/queries.py`](backend/app/queries.py).
- The Streamlit frontend ([app.py](app.py)) consumes the API to render maps, charts and tables.

## Architecture
- Data extraction & transformation: backend/scripts/load_data.py -> creates tables and views:
  - `candidates`, `party_seat_summary`, `state_turnout`, `gender_representation`, `party_vote_share`, `victory_margins`, `candidate_lookup` (see [`backend/scripts/load_data.py`](backend/scripts/load_data.py)).
  - Creates indices and views including `party_year_delta`.
- API layer: FastAPI app in [`backend/app/main.py`](backend/app/main.py). Key endpoints:
  - GET /filters -> [`backend.app.main.get_filters`](backend/app/main.py)
  - GET /party-seat-share -> [`backend.app.main.party_seat_share`](backend/app/main.py)
  - GET /state-turnout -> [`backend.app.main.state_turnout`](backend/app/main.py)
  - GET /gender-representation -> [`backend.app.main.gender_representation`](backend/app/main.py)
  - GET /top-vote-share -> [`backend.app.main.top_vote_share`](backend/app/main.py)
  - GET /margin-distribution -> [`backend.app.main.margin_distribution`](backend/app/main.py)
  - Analytics endpoints under `/analytics/*` (implemented in [`backend/app/main.py`](backend/app/main.py) and backed by [`backend/app/queries.py`](backend/app/queries.py))
- Frontend: Streamlit app [app.py](app.py) calls the API via `api_get` and renders charts (Plotly).

## Setup & run

Prereqs
- Python 3.10+ recommended
- Git (optional)
- Internet for GeoJSON used by the frontend

Install dependencies
- Backend:
  - python -m venv .venv && source .venv/bin/activate (or windows equivalent)
  - pip install -r backend/requirements.txt
- Frontend:
  - pip install -r requirements.txt

Load data (create SQLite DB)
- From project root:
  - python backend/scripts/load_data.py --csv All_States_GE.csv --db data/elections.db
  - This runs [`backend.scripts.load_data.load_database`](backend/scripts/load_data.py) which reads the CSV, cleans it and writes tables/views to `data/elections.db`.

Run backend
- From project root:
  - uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
  - The app uses database settings in [`backend/app/config.py`](backend/app/config.py) and session helper [`backend/app/database.py`](backend/app/database.py).

Run frontend (Streamlit)
- Ensure backend is running and reachable.
- Optional: set env var to point Streamlit at backend:
  - Windows: set ELECTIONS_API_URL=http://127.0.0.1:8000
  - Unix: export ELECTIONS_API_URL=http://127.0.0.1:8000
- Launch:
  - streamlit run app.py

## Useful developer notes
- API parameter building and client calls in frontend are in [`app.build_params`](app.py) and [`app.api_get`](app.py).
- The analytics endpoints call query helpers like [`backend.app.queries.vote_share_trend`](backend/app/queries.py) and [`backend.app.queries.education_win_rate`](backend/app/queries.py).
- Search is implemented by [`backend.app.queries.search_candidates`](backend/app/queries.py) and exposed at `/search` (see [`backend/app/main.py`](backend/app/main.py)).
- Database connection uses SQLAlchemy engine config in [`backend/app/database.py`](backend/app/database.py).

## Data format & caveats
- CSV header available in [All_States_GE.csv](All_States_GE.csv). Loader maps many columns in [`backend/scripts/load_data.py`](backend/scripts/load_data.py) via `COLUMN_MAP`.
- Loader coerces numeric and boolean columns (`NUMERIC_COLS`, `BOOL_COLS`) and derives columns such as `is_winner`, `gender`, `education`.
- Some fields may be null or inconsistent in source CSV; loader uses coercion and fills (see `_clean_dataframe` in [`backend/scripts/load_data.py`](backend/scripts/load_data.py)).

## Troubleshooting
- "CSV not found" — confirm path to `All_States_GE.csv`. The loader will raise FileNotFoundError if missing.
- API errors — confirm `data/elections.db` exists and uvicorn has access.
- Frontend blank maps — the frontend fetches GeoJSON from external URL; ensure internet access or swap `INDIA_GEOJSON_URL` in [app.py](app.py).

## Extending
- Add new analytics by adding SQL in [`backend/app/queries.py`](backend/app/queries.py) and exposing an endpoint in [`backend/app/main.py`](backend/app/main.py) with a corresponding schema in [`backend/app/schemas.py`](backend/app/schemas.py).
- To regenerate DB after schema changes, re-run the loader: [`backend.scripts.load_data.load_database`](backend/scripts/load_data.py).

## Contact / Credits
- Data source: TCPD / LokDhaba (CSV: [All_States_GE.csv](All_States_GE.csv))
- Project provided as a local analytic dashboard (Streamlit + FastAPI + SQLite).
