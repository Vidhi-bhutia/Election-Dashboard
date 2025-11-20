import axios from "axios";
import type {
  CandidateLookup,
  CloseContestAnswer,
  EducationWinRateAnswer,
  FilterState,
  FiltersResponse,
  GenderRepresentation,
  MarginRecord,
  PartySeatShare,
  SeatChangeAnswer,
  StateTurnout,
  TurnoutAnswer,
  VoteShare,
  VoteShareTrendAnswer,
  WomenParticipationAnswer,
} from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
});

export const fetchFilters = async (): Promise<FiltersResponse> => {
  const { data } = await api.get<FiltersResponse>("/filters");
  return data;
};

export const fetchPartySeatShare = async (
  filters: FilterState,
): Promise<PartySeatShare[]> => {
  const params: Record<string, unknown> = {};
  if (filters.year) params.year = filters.year;
  if (filters.state) params.state = filters.state;
  if (filters.gender) params.gender = filters.gender;
  if (filters.parties.length) params.parties = filters.parties;
  const { data } = await api.get<PartySeatShare[]>("/party-seat-share", {
    params,
  });
  return data;
};

export const fetchStateTurnout = async (
  filters: FilterState,
): Promise<StateTurnout[]> => {
  const params: Record<string, unknown> = {};
  if (filters.year) params.year = filters.year;
  if (filters.state) params.state = filters.state;
  const { data } = await api.get<StateTurnout[]>("/state-turnout", {
    params,
  });
  return data;
};

export const fetchGenderRepresentation = async (
  filters: FilterState,
): Promise<GenderRepresentation[]> => {
  const params: Record<string, unknown> = {};
  if (filters.year) params.year = filters.year;
  const { data } = await api.get<GenderRepresentation[]>(
    "/gender-representation",
    { params },
  );
  return data;
};

export const fetchTopVoteShare = async (
  filters: FilterState,
  limit = 5,
): Promise<VoteShare[]> => {
  const params: Record<string, unknown> = {
    limit,
    year: filters.year ?? new Date().getFullYear(),
  };
  const { data } = await api.get<VoteShare[]>("/top-vote-share", { params });
  return data;
};

export const fetchMargins = async (
  filters: FilterState,
): Promise<MarginRecord[]> => {
  const params: Record<string, unknown> = {};
  if (filters.year) params.year = filters.year;
  if (filters.state) params.state = filters.state;
  if (filters.constituency) params.constituency = filters.constituency;
  const { data } = await api.get<MarginRecord[]>("/margin-distribution", {
    params,
  });
  return data;
};

export const searchCandidates = async (
  query: string,
  filters: FilterState,
): Promise<CandidateLookup[]> => {
  if (!query.trim()) {
    return [];
  }
  const params: Record<string, unknown> = { query };
  if (filters.year) params.year = filters.year;
  if (filters.state) params.state = filters.state;
  if (filters.gender) params.gender = filters.gender;
  if (filters.constituency) params.constituency = filters.constituency;
  if (filters.parties.length === 1) {
    params.party = filters.parties[0];
  }
  const { data } = await api.get<CandidateLookup[]>("/search", { params });
  return data;
};

export const fetchHighestTurnout = async (): Promise<TurnoutAnswer> => {
  const { data } = await api.get<TurnoutAnswer>("/analytics/highest-turnout");
  return data;
};

export const fetchSeatChange = async (): Promise<SeatChangeAnswer> => {
  const { data } = await api.get<SeatChangeAnswer>("/analytics/seat-change");
  return data;
};

export const fetchWomenParticipation = async (): Promise<WomenParticipationAnswer> => {
  const { data } = await api.get<WomenParticipationAnswer>(
    "/analytics/women-participation",
  );
  return data;
};

export const fetchCloseMargins = async (): Promise<CloseContestAnswer[]> => {
  const { data } = await api.get<CloseContestAnswer[]>("/analytics/close-margins");
  return data;
};

export const fetchVoteShareTrend = async (): Promise<VoteShareTrendAnswer[]> => {
  const { data } = await api.get<VoteShareTrendAnswer[]>(
    "/analytics/vote-share-trend",
  );
  return data;
};

export const fetchEducationWinRate = async (): Promise<
  EducationWinRateAnswer[]
> => {
  const { data } = await api.get<EducationWinRateAnswer[]>(
    "/analytics/education-win-rate",
  );
  return data;
};

