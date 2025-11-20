import { useState } from "react";
import type { CandidateLookup } from "../types";

interface SearchTableProps {
  data: CandidateLookup[];
  loading?: boolean;
  onSearch: (value: string) => void;
}

const SearchTable = ({ data, loading, onSearch }: SearchTableProps) => {
  const [value, setValue] = useState("");

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSearch(value);
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Candidate / Constituency Lookup</h2>
        <form onSubmit={handleSubmit} className="search-form">
          <input
            type="text"
            placeholder="Search candidate or constituency"
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
          <button type="submit">Search</button>
        </form>
      </div>
      {loading ? (
        <div className="panel-content">Searching...</div>
      ) : data.length ? (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Year</th>
                <th>State</th>
                <th>Constituency</th>
                <th>Candidate</th>
                <th>Party</th>
                <th>Gender</th>
                <th>Votes</th>
                <th>Margin</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={`${row.year}-${row.constituency_name}-${row.candidate_name}`}>
                  <td>{row.year}</td>
                  <td>{row.state_name}</td>
                  <td>{row.constituency_name}</td>
                  <td>{row.candidate_name}</td>
                  <td>{row.party}</td>
                  <td>{row.gender ?? "NA"}</td>
                  <td>{row.votes.toLocaleString()}</td>
                  <td>{row.margin?.toLocaleString() ?? "N/A"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="panel-content">Enter a term with at least 3 characters.</div>
      )}
    </div>
  );
};

export default SearchTable;

