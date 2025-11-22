# Cleaned Dataset & Schema Documentation

Summary
- Cleaned dataset is produced by the loader function [`backend.scripts.load_data.load_database`](backend/scripts/load_data.py) and persisted at `data/elections.db`.
- The loader maps source CSV columns using [`backend.scripts.load_data.COLUMN_MAP`](backend/scripts/load_data.py) and coerces numeric and boolean fields using [`backend.scripts.load_data.NUMERIC_COLS`](backend/scripts/load_data.py) and [`backend.scripts.load_data.BOOL_COLS`](backend/scripts/load_data.py).

Files / tables produced
- candidates — full cleaned rows from the CSV (derived columns: `is_winner`, `party_class`, `education`, normalized `state_name`, `constituency_name`).
- party_seat_summary — generated from winners grouped by `year, party, state_name`.
- state_turnout — average turnout per state/year with `turnout_pct`, `electors`, `valid_votes`.
- gender_representation — per-year gender counts and `total_winners`.
- party_vote_share — aggregated votes per party/year.
- victory_margins — winner-only table with `year, state_name, constituency_name, party, margin`.
- candidate_lookup — trimmed search table used by the API.

How to reproduce
1. Ensure CSV exists: `All_States_GE.csv`.
2. Create DB and tables:
   python backend/scripts/load_data.py --csv All_States_GE.csv --db data/elections.db
   (uses [`backend.scripts.load_data.load_database`](backend/scripts/load_data.py))

Key schema notes
- Types: numeric columns are cast using `NUMERIC_COLS` and boolean columns via `BOOL_COLS` (see [backend/scripts/load_data.py](backend/scripts/load_data.py)).
- Derived flags:
  - `is_winner = position == 1`
  - `deposit_lost` coerced from "yes"/"no"
- Null handling: loader drops records missing `year`, `state_name`, or `constituency_name`; fills party with "IND".
- Views & indices: loader creates indices on `candidates(year/state/party)` and view `party_year_delta` (see SQL in [backend/scripts/load_data.py](backend/scripts/load_data.py)).

Where to inspect
- Raw CSV header: [All_States_GE.csv](All_States_GE.csv)
- Loader implementation: [`backend/scripts/load_data.py`](backend/scripts/load_data.py)
- Result DB: `data/elections.db` (SQLite)