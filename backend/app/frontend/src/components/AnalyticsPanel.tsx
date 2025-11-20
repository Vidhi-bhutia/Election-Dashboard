import type {
  CloseContestAnswer,
  EducationWinRateAnswer,
  SeatChangeAnswer,
  TurnoutAnswer,
  VoteShareTrendAnswer,
  WomenParticipationAnswer,
} from "../types";

interface AnalyticsPanelProps {
  turnout?: TurnoutAnswer;
  seatChange?: SeatChangeAnswer;
  women?: WomenParticipationAnswer;
  closeMargins?: CloseContestAnswer[];
  voteShareTrend?: VoteShareTrendAnswer[];
  education?: EducationWinRateAnswer[];
  loading?: boolean;
}

const AnalyticsPanel = ({
  turnout,
  seatChange,
  women,
  closeMargins,
  voteShareTrend,
  education,
  loading,
}: AnalyticsPanelProps) => {
  if (loading) {
    return <div className="panel-content">Loading analytical highlights...</div>;
  }
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Analytical Highlights</h2>
      </div>
      <div className="analytics-grid">
        <article>
          <h3>Highest Turnout (Latest)</h3>
          {turnout ? (
            <p>
              {turnout.state_name} recorded the highest turnout at{" "}
              <strong>{turnout.turnout_pct.toFixed(2)}%</strong> in{" "}
              {turnout.year}.
            </p>
          ) : (
            <p>Data unavailable.</p>
          )}
        </article>
        <article>
          <h3>Biggest Seat Swing</h3>
          {seatChange ? (
            <p>
              {seatChange.party} saw a swing of{" "}
              <strong>
                {seatChange.seat_change > 0 ? "+" : ""}
                {seatChange.seat_change}
              </strong>{" "}
              seats in {seatChange.year}.
            </p>
          ) : (
            <p>Data unavailable.</p>
          )}
        </article>
        <article>
          <h3>Women Participation</h3>
          {women ? (
            <p>
              Women represented{" "}
              <strong>{women.percentage.toFixed(2)}%</strong> of all candidates
              between 1991-2019.
            </p>
          ) : (
            <p>Data unavailable.</p>
          )}
        </article>
        <article className="span-2">
          <h3>Closest Contests</h3>
          {closeMargins?.length ? (
            <ul>
              {closeMargins.map((item) => (
                <li key={`${item.year}-${item.constituency_name}`}>
                  {item.constituency_name}, {item.state_name} ({item.year}) –{" "}
                  <strong>{item.margin.toLocaleString()} votes</strong>
                </li>
              ))}
            </ul>
          ) : (
            <p>No close contests found.</p>
          )}
        </article>
        <article>
          <h3>National vs Regional Vote Share</h3>
          {voteShareTrend?.length ? (
            <div className="mini-table">
              {voteShareTrend
                .filter((item) => item.year === Math.max(...voteShareTrend.map((d) => d.year)))
                .map((item) => (
                  <div key={item.category}>
                    <strong>{item.category}</strong>
                    <span>{item.vote_pct.toFixed(1)}%</span>
                  </div>
                ))}
            </div>
          ) : (
            <p>Trend unavailable.</p>
          )}
        </article>
        <article>
          <h3>Education & Win Rate</h3>
          {education?.length ? (
            <ul>
              {education.slice(0, 3).map((item) => (
                <li key={item.education}>
                  {item.education}: <strong>{item.win_rate.toFixed(1)}%</strong>
                </li>
              ))}
            </ul>
          ) : (
            <p>No education data.</p>
          )}
        </article>
      </div>
    </section>
  );
};

export default AnalyticsPanel;

