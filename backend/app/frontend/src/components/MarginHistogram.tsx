import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MarginRecord } from "../types";

interface MarginHistogramProps {
  data: MarginRecord[];
  loading?: boolean;
}

const bins = [
  { label: "<1k", max: 1000 },
  { label: "1k-5k", max: 5000 },
  { label: "5k-10k", max: 10000 },
  { label: "10k-25k", max: 25000 },
  { label: "25k-50k", max: 50000 },
  { label: "50k-100k", max: 100000 },
  { label: ">100k", max: Infinity },
];

const MarginHistogram = ({ data, loading }: MarginHistogramProps) => {
  if (loading) {
    return <div className="panel-content">Loading margins...</div>;
  }
  if (!data.length) {
    return <div className="panel-content">No margin data.</div>;
  }

  const counts = bins.map(() => 0);
  data.forEach((row) => {
    if (row.margin == null) {
      return;
    }
    const index = bins.findIndex((bin) => row.margin <= bin.max);
    const targetIndex = index === -1 ? bins.length - 1 : index;
    counts[targetIndex] += 1;
  });

  const histogram = bins.map((bin, index) => ({
    label: bin.label,
    count: counts[index],
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={histogram}>
        <XAxis dataKey="label" />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="count" fill="#6a5acd" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default MarginHistogram;

