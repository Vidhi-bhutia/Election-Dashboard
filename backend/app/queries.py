from __future__ import annotations

from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def _collect_list(db: Session, sql: str):
    rows = db.execute(text(sql)).all()
    return [row[0] for row in rows if row[0] is not None]


def get_filters(db: Session):
    return {
        "years": sorted(_collect_list(db, "SELECT DISTINCT year FROM candidates")),
        "states": sorted(_collect_list(db, "SELECT DISTINCT state_name FROM candidates")),
        "parties": sorted(_collect_list(db, "SELECT DISTINCT party FROM candidates")),
        "genders": sorted(_collect_list(db, "SELECT DISTINCT gender FROM candidates")),
        "constituencies": sorted(
            _collect_list(db, "SELECT DISTINCT constituency_name FROM candidates")
        ),
    }


def party_seat_share(
    db: Session,
    year: Optional[int] = None,
    state: Optional[str] = None,
    parties: Optional[List[str]] = None,
    gender: Optional[str] = None,
):
    sql = """
        SELECT year, party, state_name, COUNT(*) AS seats
        FROM candidates
        WHERE is_winner = 1
    """
    params = {}
    filters = []
    if year:
        filters.append("year = :year")
        params["year"] = year
    if state:
        filters.append("state_name = :state_name")
        params["state_name"] = state
    if parties:
        filters.append("party IN :parties")
        params["parties"] = tuple(parties)
    if gender:
        filters.append("gender = :gender")
        params["gender"] = gender
    if filters:
        sql += " AND " + " AND ".join(filters)
    sql += " GROUP BY year, party, state_name ORDER BY year, seats DESC"
    result = db.execute(text(sql), params).mappings().all()
    return result


def state_turnout(db: Session, year: Optional[int] = None, state: Optional[str] = None):
    sql = "SELECT year, state_name, turnout_pct, electors, valid_votes FROM state_turnout"
    params = {}
    filters = []
    if year:
        filters.append("year = :year")
        params["year"] = year
    if state:
        filters.append("state_name = :state_name")
        params["state_name"] = state
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY year, turnout_pct DESC"
    return db.execute(text(sql), params).mappings().all()


def gender_representation(db: Session, year: Optional[int] = None):
    sql = "SELECT year, gender, total_candidates, total_winners FROM gender_representation"
    params = {}
    if year:
        sql += " WHERE year = :year"
        params["year"] = year
    sql += " ORDER BY year, gender"
    return db.execute(text(sql), params).mappings().all()


def top_vote_share(db: Session, year: int, limit: int = 5):
    sql = """
        WITH totals AS (
            SELECT total_votes,
                   SUM(total_votes) OVER (PARTITION BY year) AS year_total,
                   party,
                   year
            FROM party_vote_share
            WHERE year = :year
        )
        SELECT party, year, total_votes, (total_votes * 100.0 / year_total) AS vote_pct
        FROM totals
        ORDER BY total_votes DESC
        LIMIT :limit
    """
    return db.execute(text(sql), {"year": year, "limit": limit}).mappings().all()


def margin_distribution(
    db: Session,
    year: Optional[int] = None,
    state: Optional[str] = None,
    constituency: Optional[str] = None,
):
    sql = "SELECT year, state_name, constituency_name, party, margin FROM victory_margins"
    params = {}
    filters = []
    if year:
        filters.append("year = :year")
        params["year"] = year
    if state:
        filters.append("state_name = :state_name")
        params["state_name"] = state
    if constituency:
        filters.append("constituency_name = :constituency")
        params["constituency"] = constituency
    if filters:
        sql += " WHERE " + " AND ".join(filters)
    sql += " ORDER BY margin ASC"
    return db.execute(text(sql), params).mappings().all()


def search_candidates(
    db: Session,
    query: str,
    year: Optional[int] = None,
    state: Optional[str] = None,
    party: Optional[str] = None,
    gender: Optional[str] = None,
    constituency: Optional[str] = None,
    limit: int = 20,
):
    sql = """
        SELECT year, state_name, constituency_name, candidate_name, party, gender, position, votes, margin
        FROM candidate_lookup
        WHERE (candidate_name LIKE :query OR constituency_name LIKE :query)
    """
    params = {"query": f"%{query}%", "limit": limit}
    if year:
        sql += " AND year = :year"
        params["year"] = year
    if state:
        sql += " AND state_name = :state_name"
        params["state_name"] = state
    if party:
        sql += " AND party = :party"
        params["party"] = party
    if gender:
        sql += " AND gender = :gender"
        params["gender"] = gender
    if constituency:
        sql += " AND constituency_name = :constituency"
        params["constituency"] = constituency
    sql += " ORDER BY year DESC LIMIT :limit"
    return db.execute(text(sql), params).mappings().all()


def highest_turnout(db: Session):
    sql = """
        SELECT state_name, turnout_pct, year
        FROM state_turnout
        WHERE year = (SELECT MAX(year) FROM state_turnout)
        ORDER BY turnout_pct DESC
        LIMIT 1
    """
    return db.execute(text(sql)).mappings().first()


def biggest_seat_change(db: Session):
    sql = """
        SELECT party, year, seat_change
        FROM party_year_delta
        ORDER BY ABS(seat_change) DESC
        LIMIT 1
    """
    return db.execute(text(sql)).mappings().first()


def women_participation(db: Session):
    sql = """
        WITH totals AS (
            SELECT gender,
                   COUNT(*) AS total
            FROM candidates
            GROUP BY gender
        )
        SELECT (SELECT total FROM totals WHERE gender = 'F') * 100.0 / SUM(total) AS percentage
        FROM totals
    """
    return db.execute(text(sql)).mappings().first()


def closest_margins(db: Session, limit: int = 5):
    sql = """
        SELECT constituency_name, state_name, year, margin
        FROM victory_margins
        WHERE margin > 0
        ORDER BY margin ASC
        LIMIT :limit
    """
    return db.execute(text(sql), {"limit": limit}).mappings().all()


def vote_share_trend(db: Session):
    sql = """
        WITH classified AS (
            SELECT year,
                   CASE
                       WHEN party_type LIKE '%National%' THEN 'National'
                       WHEN party_type LIKE '%State%' THEN 'Regional'
                       ELSE 'Other'
                   END AS category,
                   SUM(votes) AS votes
            FROM candidates
            GROUP BY year, category
        ),
        totals AS (
            SELECT year, SUM(votes) AS total_votes
            FROM classified
            GROUP BY year
        )
        SELECT c.year,
               c.category,
               CASE WHEN t.total_votes = 0 OR t.total_votes IS NULL
                    THEN 0
                    ELSE COALESCE(c.votes, 0) * 100.0 / t.total_votes
               END AS vote_pct
        FROM classified c
        JOIN totals t ON c.year = t.year
        ORDER BY c.year, c.category
    """
    return db.execute(text(sql)).mappings().all()


def education_win_rate(db: Session):
    sql = """
        WITH summary AS (
            SELECT education,
                   COUNT(*) AS candidates,
                   SUM(CASE WHEN is_winner = 1 THEN 1 ELSE 0 END) AS winners
            FROM candidates
            WHERE education IS NOT NULL
            GROUP BY education
            HAVING candidates >= 50
        )
        SELECT education, winners * 100.0 / candidates AS win_rate
        FROM summary
        ORDER BY win_rate DESC
        LIMIT 10
    """
    return db.execute(text(sql)).mappings().all()

