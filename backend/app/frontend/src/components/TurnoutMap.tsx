import { useMemo } from "react";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import type { StateTurnout } from "../types";

const INDIA_GEO_URL =
  "https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson";

interface TurnoutMapProps {
  data: StateTurnout[];
  loading?: boolean;
}

const palette = ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"];

const normalize = (value: string) =>
  value.toLowerCase().replace(/[^a-z]/g, "");

const TurnoutMap = ({ data, loading }: TurnoutMapProps) => {
  const { min, max, byState } = useMemo(() => {
    if (!data.length) {
      return { min: 0, max: 0, byState: new Map<string, StateTurnout>() };
    }
    const values = data.map((item) => item.turnout_pct);
    const byStateMap = new Map<string, StateTurnout>();
    data.forEach((item) => {
      byStateMap.set(normalize(item.state_name), item);
    });
    return {
      min: Math.min(...values),
      max: Math.max(...values),
      byState: byStateMap,
    };
  }, [data]);

  const getColor = (value?: number) => {
    if (!value || max === min) {
      return palette[0];
    }
    const ratio = (value - min) / (max - min);
    const index = Math.min(
      palette.length - 1,
      Math.floor(ratio * palette.length),
    );
    return palette[index];
  };

  if (loading) {
    return <div className="panel-content">Loading turnout map...</div>;
  }
  if (!data.length) {
    return <div className="panel-content">No turnout data.</div>;
  }

  return (
    <div className="map-wrapper">
      <ComposableMap projectionConfig={{ scale: 1000, center: [82, 22] }}>
        <Geographies geography={INDIA_GEO_URL}>
          {({ geographies }: { geographies: any[] }) =>
            geographies.map((geo: any) => {
              const stateName = (geo.properties.NAME_1 ?? "") as string;
              const info = byState.get(normalize(stateName));
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={getColor(info?.turnout_pct)}
                >
                  <title>
                    {stateName}: {info ? `${info.turnout_pct.toFixed(2)}%` : "N/A"}
                  </title>
                </Geography>
              );
            })
          }
        </Geographies>
      </ComposableMap>
      <div className="legend">
        {palette.map((color, index) => (
          <span key={color}>
            <i style={{ background: color }} />
            {index === 0
              ? "Lower turnout"
              : index === palette.length - 1
                ? "Higher turnout"
                : ""}
          </span>
        ))}
      </div>
    </div>
  );
};

export default TurnoutMap;

