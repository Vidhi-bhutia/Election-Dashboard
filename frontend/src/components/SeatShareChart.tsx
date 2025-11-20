import {
  Bar,
  BarChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PartySeatShare } from "../types";

interface SeatShareChartProps {
  data: PartySeatShare[];
  selectedParties: string[];
  loading?: boolean;
}

const colors = ["#2f7ed8", "#8bbc21", "#910000", "#492970", "#f28f43", "#77a1e5"];

const SeatShareChart = ({ data, selectedParties, loading }: SeatShareChartProps) => {
  if (loading) {
    return <div className="panel-content">Loading seat share...</div>;
  }
  if (!data.length) {
    return <div className="panel-content">No data for selected filters.</div>;
  }

  const totals = data.reduce<Record<string, number>>((acc, row) => {
    acc[row.party] = (acc[row.party] ?? 0) + row.seats;
    return acc;
  }, {});

  const parties =
    selectedParties.length > 0
      ? selectedParties
      : Object.entries(totals)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 6)
          .map(([party]) => party);

  const years = Array.from(new Set(data.map((row) => row.year))).sort(
    (a, b) => a - b,
  );

  const chartData = years.map((year) => {
    const rows = data.filter((row) => row.year === year);
    const entry: Record<string, number | string> = { year };
    parties.forEach((party) => {
      entry[party] = rows
        .filter((row) => row.party === party)
        .reduce((sum, row) => sum + row.seats, 0);
    });
    return entry;
  });

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={chartData} stackOffset="expand">
        <XAxis dataKey="year" />
        <YAxis tickFormatter={(value) => `${Math.round(value * 100)}%`} />
        <Tooltip formatter={(value: number) => `${(value * 100).toFixed(1)}%`} />
        <Legend />
        {parties.map((party, index) => (
          <Bar
            key={party}
            dataKey={party}
            stackId="seats"
            fill={colors[index % colors.length]}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
};

export default SeatShareChart;

