export interface FiltersResponse {
  years: number[];
  states: string[];
  parties: string[];
  genders: string[];
  constituencies: string[];
}

export interface FilterState {
  year?: number | null;
  state?: string | null;
  parties: string[];
  gender?: string | null;
  constituency?: string | null;
}

export interface PartySeatShare {
  year: number;
  party: string;
  seats: number;
  state_name?: string | null;
}

export interface StateTurnout {
  year: number;
  state_name: string;
  turnout_pct: number;
  electors: number;
  valid_votes: number;
}

export interface GenderRepresentation {
  year: number;
  gender: string;
  total_candidates: number;
  total_winners: number;
}

export interface VoteShare {
  year: number;
  party: string;
  total_votes: number;
  vote_pct: number;
}

export interface MarginRecord {
  year: number;
  state_name: string;
  constituency_name: string;
  party: string;
  margin: number;
}

export interface CandidateLookup {
  year: number;
  state_name: string;
  constituency_name: string;
  candidate_name: string;
  party: string;
  gender?: string | null;
  position: number;
  votes: number;
  margin?: number | null;
}

export interface TurnoutAnswer {
  state_name: string;
  turnout_pct: number;
  year: number;
}

export interface SeatChangeAnswer {
  party: string;
  year: number;
  seat_change: number;
}

export interface WomenParticipationAnswer {
  percentage: number;
}

export interface CloseContestAnswer {
  constituency_name: string;
  state_name: string;
  year: number;
  margin: number;
}

export interface VoteShareTrendAnswer {
  category: string;
  year: number;
  vote_pct: number;
}

export interface EducationWinRateAnswer {
  education: string;
  win_rate: number;
}

