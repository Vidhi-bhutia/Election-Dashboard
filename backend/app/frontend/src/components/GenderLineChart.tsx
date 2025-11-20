import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { GenderRepresentation } from "../types";

interface GenderLineChartProps {
  data: GenderRepresentation[];
  loading?: boolean;
  focusGender?: string | null;
}

const GenderLineChart = ({
  data,
  loading,
  focusGender,
}: GenderLineChartProps) => {
  if (loading) {
    return <div className="panel-content">Loading gender trends...</div>;
  }
  if (!data.length) {
    return <div className="panel-content">No gender data.</div>;
  }

  const years = Array.from(new Set(data.map((row) => row.year))).sort();
  const chartData = years.map((year) => {
    const entry: Record<string, number | string> = { year };
    data
      .filter((row) => row.year === year)
      .forEach((row) => {
        const label = row.gender === "F" ? "female" : row.gender === "M" ? "male" : "other";
        entry[`${label}Candidates`] = row.total_candidates;
        entry[`${label}Winners`] = row.total_winners;
      });
    return entry;
  });

  const lines = [
    { key: "femaleCandidates", color: "#d14a73", label: "Women Candidates" },
    { key: "maleCandidates", color: "#1f77b4", label: "Men Candidates" },
  ];

  const filteredLines = focusGender
    ? lines.filter((line) =>
        focusGender === "F"
          ? line.key.startsWith("female")
          : focusGender === "M"
            ? line.key.startsWith("male")
            : true,
      )
    : lines;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <XAxis dataKey="year" />
        <YAxis allowDecimals={false} />
        <Tooltip
          formatter={(value, name) =>
            Array.isArray(value) ? value : [`${value}`, name]
          }
        />
        {filteredLines.map((line) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            stroke={line.color}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default GenderLineChart;

