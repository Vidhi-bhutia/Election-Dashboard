from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class PartySeatShare(BaseModel):
    year: int
    party: str
    seats: int
    state_name: Optional[str] = None


class StateTurnout(BaseModel):
    year: int
    state_name: str
    turnout_pct: float
    electors: int
    valid_votes: int


class GenderRepresentation(BaseModel):
    year: int
    gender: str
    total_candidates: int
    total_winners: int


class VoteShare(BaseModel):
    year: int
    party: str
    total_votes: int
    vote_pct: float


class MarginRecord(BaseModel):
    year: int
    state_name: str
    constituency_name: str
    party: str
    margin: int


class CandidateLookup(BaseModel):
    year: int
    state_name: str
    constituency_name: str
    candidate_name: str
    party: str
    gender: Optional[str]
    position: int
    votes: int
    margin: Optional[int]


class FiltersResponse(BaseModel):
    years: List[int]
    states: List[str]
    parties: List[str]
    genders: List[str]
    constituencies: List[str]


class TurnoutAnswer(BaseModel):
    state_name: str
    turnout_pct: float
    year: int


class SeatChangeAnswer(BaseModel):
    party: str
    year: int
    seat_change: int


class WomenParticipationAnswer(BaseModel):
    percentage: float


class CloseContestAnswer(BaseModel):
    constituency_name: str
    state_name: str
    year: int
    margin: int


class VoteShareTrendAnswer(BaseModel):
    category: str
    year: int
    vote_pct: float


class EducationWinRateAnswer(BaseModel):
    education: str
    win_rate: float

