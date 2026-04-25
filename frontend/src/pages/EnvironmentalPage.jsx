import { useState } from "react";
import CitySelector from "../components/CitySelector";
import RooftopMap from "../components/RooftopMap";
import RooftopTable from "../components/RooftopTable";
import StatCard from "../components/StatCard";
import { useCityRooftops, useCityRooftopsTable, useCityStats } from "../hooks/useCityData";

export default function EnvironmentalPage({ cityCode, setCityCode }) {
  const [metric, setMetric] = useState("co2_balance");
  const { data: geojson } = useCityRooftops(cityCode);
  const { data: rows = [] } = useCityRooftopsTable(cityCode);
  const { data: stats } = useCityStats(cityCode);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Environmental Indicators</h1>
        <div className="flex items-center gap-3">
          <select
            className="border border-slate-300 rounded px-2 py-1.5 text-sm bg-white"
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
          >
            <option value="co2_balance">Net CO₂ balance</option>
            <option value="co2_seq">CO₂ sequestration</option>
            <option value="co2_emis">CO₂ emissions</option>
          </select>
          <CitySelector value={cityCode} onChange={setCityCode} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <StatCard label="CO₂ sequestered (t)" value={fmt(stats?.total_co2_seq_t, 2)} />
        <StatCard label="CO₂ emitted (t)" value={fmt(stats?.total_co2_emis_t, 2)} />
        <StatCard label="Net CO₂ (t)" value={fmt(stats?.net_co2_balance_t, 2)} />
      </div>

      <div className="h-[420px]">
        <RooftopMap geojson={geojson} cityCode={cityCode} metric={metric} />
      </div>

      <RooftopTable
        rows={rows}
        columns={[
          { key: "id", label: "ID" },
          { key: "commune_name", label: "Commune" },
          { key: "technique", label: "Technique" },
          { key: "environmental.crop_dry_matter_kg", label: "Dry matter (kg)", numeric: true, digits: 0 },
          { key: "environmental.co2_seq_kg", label: "CO₂ seq. (kg)", numeric: true, digits: 0 },
          { key: "environmental.co2_emissions_kg", label: "CO₂ emis. (kg)", numeric: true, digits: 0 },
          { key: "environmental.net_co2_balance_kg", label: "Net CO₂ (kg)", numeric: true, digits: 0 },
        ]}
      />
    </div>
  );
}

function fmt(v, d = 0) {
  if (v == null) return "—";
  return Number(v).toLocaleString(undefined, { maximumFractionDigits: d });
}
