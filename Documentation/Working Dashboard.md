# Deliverable B — Working Dashboard (how to run & host)

Overview
- Frontend: Streamlit app at [app.py](app.py).
- Backend: FastAPI app at [backend/app/main.py](backend/app/main.py) exposing REST endpoints consumed by the frontend.

Local run (recommended)
1. Backend
   - Create & activate virtualenv.
   - Install backend deps: pip install -r backend/requirements.txt
   - Ensure DB exists: run loader (see [`backend.scripts.load_data.load_database`](backend/scripts/load_data.py)).
   - Start server:
     uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   - Swagger UI available at: http://127.0.0.1:8000/docs

2. Frontend
   - Install frontend deps: pip install -r requirements.txt
   - Optionally point to API:
     - Windows: set ELECTIONS_API_URL=http://127.0.0.1:8000
     - Unix: export ELECTIONS_API_URL=http://127.0.0.1:8000
   - Start Streamlit:
     streamlit run app.py
   - Dashboard is interactive and uses [`app.api_get`](app.py) and [`app.fetch_geojson`](app.py) for maps.

Free cloud hosting options (short)
- FastAPI: deploy to Render / Fly / Railway; ensure `data/elections.db` is included or use a cloud DB.
- Streamlit Cloud: deploy `app.py` after enabling network access to backend OR containerize both and use a single host.
- If hosting backend externally, update `ELECTIONS_API_URL` in Streamlit environment.

Files to review
- Frontend: [app.py](app.py)
- Backend: [backend/app/main.py](backend/app/main.py), [backend/app/config.py](backend/app/config.py), [backend/app/database.py](backend/app/database.py)