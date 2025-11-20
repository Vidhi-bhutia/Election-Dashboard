import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import "./App.css";
import FilterPanel from "./components/FilterPanel";
import SeatShareChart from "./components/SeatShareChart";
import TurnoutMap from "./components/TurnoutMap";
import GenderLineChart from "./components/GenderLineChart";
import VoteShareDonut from "./components/VoteShareDonut";
import MarginHistogram from "./components/MarginHistogram";
import SearchTable from "./components/SearchTable";
import AnalyticsPanel from "./components/AnalyticsPanel";
import {
  fetchCloseMargins,
  fetchEducationWinRate,
  fetchFilters,
  fetchGenderRepresentation,
  fetchHighestTurnout,
  fetchMargins,
  fetchPartySeatShare,
  fetchSeatChange,
  fetchStateTurnout,
  fetchTopVoteShare,
  fetchVoteShareTrend,
  fetchWomenParticipation,
  searchCandidates,
} from "./api";
import type { FilterState } from "./types";

const baseFilters: FilterState = {
  year: null,
  state: null,
  parties: [],
  gender: null,
  constituency: null,
};

function App() {
  const [filters, setFilters] = useState<FilterState>(baseFilters);
  const [searchTerm, setSearchTerm] = useState("");

  const { data: filterOptions, isLoading: filtersLoading } = useQuery({
    queryKey: ["filters"],
    queryFn: fetchFilters,
  });

  const latestYear = filterOptions?.years.at(-1) ?? null;

  useEffect(() => {
    if (filterOptions && filters.year === null) {
      setFilters((prev) => ({ ...prev, year: latestYear }));
    }
  }, [filterOptions, filters.year, latestYear]);

  const resolvedFilters = useMemo(
    () => ({
      ...filters,
      year: filters.year ?? latestYear,
    }),
    [filters, latestYear],
  );

  const seatShareQuery = useQuery({
    queryKey: [
      "seat-share",
      resolvedFilters.year,
      resolvedFilters.state,
      resolvedFilters.gender,
      resolvedFilters.parties.slice().sort().join("|"),
    ],
    queryFn: () => fetchPartySeatShare(resolvedFilters),
    enabled: Boolean(resolvedFilters.year),
  });

  const turnoutQuery = useQuery({
    queryKey: ["state-turnout", resolvedFilters.year, resolvedFilters.state],
    queryFn: () => fetchStateTurnout(resolvedFilters),
    enabled: Boolean(resolvedFilters.year),
  });

  const genderQuery = useQuery({
    queryKey: ["gender", resolvedFilters.year],
    queryFn: () => fetchGenderRepresentation(resolvedFilters),
  });

  const voteShareQuery = useQuery({
    queryKey: ["vote-share", resolvedFilters.year],
    queryFn: () => fetchTopVoteShare(resolvedFilters),
    enabled: Boolean(resolvedFilters.year),
  });

  const marginQuery = useQuery({
    queryKey: [
      "margins",
      resolvedFilters.year,
      resolvedFilters.state,
      resolvedFilters.constituency,
    ],
    queryFn: () => fetchMargins(resolvedFilters),
    enabled: Boolean(resolvedFilters.year),
  });

  const searchQuery = useQuery({
    queryKey: [
      "search",
      searchTerm,
      resolvedFilters.year,
      resolvedFilters.state,
      resolvedFilters.gender,
      resolvedFilters.constituency,
      resolvedFilters.parties.slice().sort().join("|"),
    ],
    queryFn: () => searchCandidates(searchTerm, resolvedFilters),
    enabled: searchTerm.trim().length >= 3,
  });

  const turnoutAnswer = useQuery({
    queryKey: ["analytics", "turnout"],
    queryFn: fetchHighestTurnout,
  });
  const seatChangeAnswer = useQuery({
    queryKey: ["analytics", "seat-change"],
    queryFn: fetchSeatChange,
  });
  const womenAnswer = useQuery({
    queryKey: ["analytics", "women"],
    queryFn: fetchWomenParticipation,
  });
  const closeMarginsAnswer = useQuery({
    queryKey: ["analytics", "close-margins"],
    queryFn: fetchCloseMargins,
  });
  const voteShareTrendAnswer = useQuery({
    queryKey: ["analytics", "vote-share-trend"],
    queryFn: fetchVoteShareTrend,
  });
  const educationAnswer = useQuery({
    queryKey: ["analytics", "education"],
    queryFn: fetchEducationWinRate,
  });

  const analyticsLoading =
    turnoutAnswer.isLoading ||
    seatChangeAnswer.isLoading ||
    womenAnswer.isLoading ||
    closeMarginsAnswer.isLoading ||
    voteShareTrendAnswer.isLoading ||
    educationAnswer.isLoading;

  const handleFilterChange = (updates: Partial<FilterState>) => {
    setFilters((prev) => ({ ...prev, ...updates }));
  };

  const handleResetFilters = () => {
    setFilters({
      ...baseFilters,
      year: latestYear,
    });
    setSearchTerm("");
  };

  return (
    <div className="app">
      <header>
        <div>
          <p className="eyebrow">Varahe Analytics · Lok Dhaba</p>
          <h1>Indian General Election Insights (1991-2019)</h1>
          <p className="subtitle">
            Track turnout, party performance, representation and razor-thin
            contests across Lok Sabha elections.
          </p>
        </div>
      </header>
      <main>
        <FilterPanel
          filters={resolvedFilters}
          options={filterOptions}
          onChange={handleFilterChange}
          onReset={handleResetFilters}
        />

        <section className="grid two-columns">
          <div className="panel">
            <div className="panel-header">
              <h2>Party Seat Share</h2>
              <p>Stacked bar shows seat distribution per election year.</p>
            </div>
            <SeatShareChart
              data={seatShareQuery.data ?? []}
              selectedParties={resolvedFilters.parties}
              loading={seatShareQuery.isLoading}
            />
          </div>
          <div className="panel">
            <div className="panel-header">
              <h2>State-wise Turnout</h2>
              <p>Choropleth for average turnout by state.</p>
            </div>
            <TurnoutMap
              data={turnoutQuery.data ?? []}
              loading={turnoutQuery.isLoading || filtersLoading}
            />
          </div>
        </section>

        <section className="grid two-columns">
          <div className="panel">
            <div className="panel-header">
              <h2>Gender Representation</h2>
              <p>Compare male vs female candidate volumes.</p>
            </div>
            <GenderLineChart
              data={genderQuery.data ?? []}
              loading={genderQuery.isLoading}
              focusGender={filters.gender}
            />
          </div>
          <div className="panel">
            <div className="panel-header">
              <h2>Top Vote Share</h2>
              <p>Leading parties by share of votes.</p>
            </div>
            <VoteShareDonut
              data={voteShareQuery.data ?? []}
              loading={voteShareQuery.isLoading}
            />
          </div>
        </section>

        <section className="grid two-columns">
          <div className="panel">
            <div className="panel-header">
              <h2>Margin of Victory Distribution</h2>
              <p>Histogram of winning margins (votes).</p>
            </div>
            <MarginHistogram
              data={marginQuery.data ?? []}
              loading={marginQuery.isLoading}
            />
          </div>
          <SearchTable
            data={searchQuery.data ?? []}
            loading={searchQuery.isFetching}
            onSearch={setSearchTerm}
          />
        </section>

        <AnalyticsPanel
          turnout={turnoutAnswer.data}
          seatChange={seatChangeAnswer.data}
          women={womenAnswer.data}
          closeMargins={closeMarginsAnswer.data}
          voteShareTrend={voteShareTrendAnswer.data}
          education={educationAnswer.data}
          loading={analyticsLoading}
        />
      </main>
    </div>
  );
}

export default App;
