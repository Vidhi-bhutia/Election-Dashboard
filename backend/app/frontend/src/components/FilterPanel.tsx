import type { FilterState, FiltersResponse } from "../types";

interface FilterPanelProps {
  filters: FilterState;
  options?: FiltersResponse;
  onChange: (updates: Partial<FilterState>) => void;
  onReset: () => void;
}

const FilterPanel = ({ filters, options, onChange, onReset }: FilterPanelProps) => {
  const handlePartyChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = Array.from(event.target.selectedOptions).map(
      (option) => option.value,
    );
    onChange({ parties: selected });
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Filters</h2>
        <button type="button" onClick={onReset}>
          Reset
        </button>
      </div>
      <div className="filter-grid">
        <label>
          Year
          <select
            value={filters.year ?? ""}
            onChange={(e) =>
              onChange({ year: e.target.value ? Number(e.target.value) : null })
            }
          >
            <option value="">All</option>
            {options?.years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </label>
        <label>
          State / UT
          <select
            value={filters.state ?? ""}
            onChange={(e) => onChange({ state: e.target.value || null })}
          >
            <option value="">All</option>
            {options?.states.map((state) => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
        </label>
        <label>
          Constituency
          <select
            value={filters.constituency ?? ""}
            onChange={(e) =>
              onChange({ constituency: e.target.value || null })
            }
          >
            <option value="">All</option>
            {options?.constituencies.map((constituency) => (
              <option key={constituency} value={constituency}>
                {constituency}
              </option>
            ))}
          </select>
        </label>
        <label>
          Gender
          <select
            value={filters.gender ?? ""}
            onChange={(e) => onChange({ gender: e.target.value || null })}
          >
            <option value="">All</option>
            {options?.genders
              .filter(Boolean)
              .map((gender) => (
                <option key={gender} value={gender}>
                  {gender}
                </option>
              ))}
          </select>
        </label>
        <label>
          Parties
          <select
            multiple
            value={filters.parties}
            onChange={handlePartyChange}
            size={4}
          >
            {options?.parties.map((party) => (
              <option key={party} value={party}>
                {party}
              </option>
            ))}
          </select>
          <small>Select multiple to compare seat share</small>
        </label>
      </div>
    </section>
  );
};

export default FilterPanel;

