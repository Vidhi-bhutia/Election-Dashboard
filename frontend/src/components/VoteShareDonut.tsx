import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { VoteShare } from "../types";

interface VoteShareDonutProps {
  data: VoteShare[];
  loading?: boolean;
}

const colors = ["#3366CC", "#DC3912", "#FF9900", "#109618", "#990099", "#0099C6"];

const VoteShareDonut = ({ data, loading }: VoteShareDonutProps) => {
  const chartData = data.map((item) => ({ ...item }));

  if (loading) {
    return <div className="panel-content">Loading vote share...</div>;
  }
  if (!data.length) {
    return <div className="panel-content">No vote share data.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData as Array<Record<string, number | string>>}
          dataKey="vote_pct"
          nameKey="party"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={4}
        >
          {data.map((entry, index) => (
            <Cell key={entry.party} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default VoteShareDonut;

