from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db
from . import queries
from . import schemas

app = FastAPI(title="Indian General Elections API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/filters", response_model=schemas.FiltersResponse)
def get_filters(db: Session = Depends(get_db)):
    data = queries.get_filters(db)
    return schemas.FiltersResponse(**data)


@app.get("/party-seat-share", response_model=List[schemas.PartySeatShare])
def party_seat_share(
    year: Optional[int] = None,
    state: Optional[str] = None,
    parties: Optional[List[str]] = Query(default=None),
    gender: Optional[str] = None,
    db: Session = Depends(get_db),
):
    result = queries.party_seat_share(db, year, state, parties, gender)
    return [schemas.PartySeatShare(**row) for row in result]


@app.get("/state-turnout", response_model=List[schemas.StateTurnout])
def state_turnout(
    year: Optional[int] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    result = queries.state_turnout(db, year, state)
    return [schemas.StateTurnout(**row) for row in result]


@app.get("/gender-representation", response_model=List[schemas.GenderRepresentation])
def gender_representation(
    year: Optional[int] = None, db: Session = Depends(get_db)
):
    result = queries.gender_representation(db, year)
    return [schemas.GenderRepresentation(**row) for row in result]


@app.get("/top-vote-share", response_model=List[schemas.VoteShare])
def top_vote_share(year: int, limit: int = 5, db: Session = Depends(get_db)):
    result = queries.top_vote_share(db, year, limit)
    return [schemas.VoteShare(**row) for row in result]


@app.get("/margin-distribution", response_model=List[schemas.MarginRecord])
def margin_distribution(
    year: Optional[int] = None,
    state: Optional[str] = None,
    constituency: Optional[str] = None,
    db: Session = Depends(get_db),
):
    result = queries.margin_distribution(db, year, state, constituency)
    return [schemas.MarginRecord(**row) for row in result]


@app.get("/search", response_model=List[schemas.CandidateLookup])
def search(
    query: str,
    year: Optional[int] = None,
    state: Optional[str] = None,
    party: Optional[str] = None,
    gender: Optional[str] = None,
    constituency: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")
    result = queries.search_candidates(db, query, year, state, party, gender, constituency, limit)
    return [schemas.CandidateLookup(**row) for row in result]


@app.get("/analytics/highest-turnout", response_model=schemas.TurnoutAnswer)
def highest_turnout(db: Session = Depends(get_db)):
    row = queries.highest_turnout(db)
    if not row:
        raise HTTPException(status_code=404, detail="No data available.")
    return schemas.TurnoutAnswer(**row)


@app.get("/analytics/seat-change", response_model=schemas.SeatChangeAnswer)
def seat_change(db: Session = Depends(get_db)):
    row = queries.biggest_seat_change(db)
    if not row:
        raise HTTPException(status_code=404, detail="No data available.")
    return schemas.SeatChangeAnswer(**row)


@app.get("/analytics/women-participation", response_model=schemas.WomenParticipationAnswer)
def women_participation(db: Session = Depends(get_db)):
    row = queries.women_participation(db)
    if not row:
        raise HTTPException(status_code=404, detail="No data available.")
    return schemas.WomenParticipationAnswer(**row)


@app.get("/analytics/close-margins", response_model=List[schemas.CloseContestAnswer])
def close_margins(limit: int = 5, db: Session = Depends(get_db)):
    data = queries.closest_margins(db, limit)
    return [schemas.CloseContestAnswer(**row) for row in data]


@app.get("/analytics/vote-share-trend", response_model=List[schemas.VoteShareTrendAnswer])
def vote_share_trend(db: Session = Depends(get_db)):
    data = queries.vote_share_trend(db)
    return [schemas.VoteShareTrendAnswer(**row) for row in data]


@app.get("/analytics/education-win-rate", response_model=List[schemas.EducationWinRateAnswer])
def education_win_rate(db: Session = Depends(get_db)):
    data = queries.education_win_rate(db)
    return [schemas.EducationWinRateAnswer(**row) for row in data]

