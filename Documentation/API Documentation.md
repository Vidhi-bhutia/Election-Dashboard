# Deliverable C — API Documentation / How to Access Swagger UI

FastAPI exposes endpoints documented by OpenAPI/Swagger when the server runs.

Open Swagger UI
- Start backend:
  uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
- Open: http://127.0.0.1:8000/docs

Key endpoints (implementation references)
- GET /filters — returns available filters
  - Implementation: [`backend.app.main.get_filters`](backend/app/main.py)
  - Schema: [`backend.app.schemas.FiltersResponse`](backend/app/schemas.py)
- GET /party-seat-share — seats by party (queryable by `year`, `state`, `parties`, `gender`)
  - Implementation: [`backend.app.main.party_seat_share`](backend/app/main.py)
  - Core SQL: handled in [`backend.app.queries.party_seat_share`](backend/app/queries.py)
- GET /state-turnout — state turnout summary
  - Implementation: [`backend.app.main.state_turnout`](backend/app/main.py)
  - Core SQL: [`backend.app.queries.state_turnout`](backend/app/queries.py)
- GET /gender-representation — candidates & winners by gender
  - Implementation: [`backend.app.main.gender_representation`](backend/app/main.py)
- GET /top-vote-share — top parties by vote share (requires `year`)
  - Implementation: [`backend.app.main.top_vote_share`](backend/app/main.py)
  - SQL: [`backend.app.queries.top_vote_share`](backend/app/queries.py)
- GET /margin-distribution — victory margins (filters: `year`, `state`, `constituency`)
  - Implementation: [`backend.app.main.margin_distribution`](backend/app/main.py)
  - SQL: [`backend.app.queries.margin_distribution`](backend/app/queries.py)
- GET /search — search candidate/constituency (query param `query` required)
  - Implementation: [`backend.app.main.search`](backend/app/main.py)
  - SQL: [`backend.app.queries.search_candidates`](backend/app/queries.py)
- Analytics endpoints under `/analytics/*`:
  - Highest turnout: [`backend.app.main.highest_turnout`](backend/app/main.py) -> [`backend.app.queries.highest_turnout`](backend/app/queries.py)
  - Seat change: [`backend.app.main.seat_change`](backend/app/main.py) -> [`backend.app.queries.biggest_seat_change`](backend/app/queries.py)
  - Women participation: [`backend.app.main.women_participation`](backend/app/main.py) -> [`backend.app.queries.women_participation`](backend/app/queries.py)
  - Close margins: [`backend.app.main.close_margins`](backend/app/main.py) -> [`backend.app.queries.closest_margins`](backend/app/queries.py)
  - Vote share trend: [`backend.app.main.vote_share_trend`](backend/app/main.py) -> [`backend.app.queries.vote_share_trend`](backend/app/queries.py)
  - Education win rate: [`backend.app.main.education_win_rate`](backend/app/main.py) -> [`backend.app.queries.education_win_rate`](backend/app/queries.py)

Example: call /filters from the frontend
- Frontend uses [`app.api_get`](app.py) to call `/filters` and the response model is [`backend.app.schemas.FiltersResponse`](backend/app/schemas.py).

Notes
- For programmatic access use query params as the frontend builds them in [`app.build_params`](app.py).
- Swagger provides request/response examples automatically when the server runs.