import CitySelector from "../components/CitySelector";
import RooftopMap from "../components/RooftopMap";
import RooftopTable from "../components/RooftopTable";
import StatCard from "../components/StatCard";
import { useCityRooftops, useCityRooftopsTable, useCityStats } from "../hooks/useCityData";

export default function SocialPage({ cityCode, setCityCode }) {
  const { data: geojson } = useCityRooftops(cityCode);
  const { data: rows = [] } = useCityRooftopsTable(cityCode);
  const { data: stats } = useCityStats(cityCode);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Social Indicators</h1>
        <CitySelector value={cityCode} onChange={setCityCode} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <StatCard label="Farmers" value={fmt(stats?.farmers)} />
        <StatCard label="Total labor (persons)" value={fmt(stats?.total_labor_persons, 2)} />
        <StatCard
          label="Empl. rate (total)"
          value={fmt(stats?.employment_rate_total_pct, 3)}
          unit="%"
        />
        <StatCard
          label="Empl. rate (unemployed)"
          value={fmt(stats?.employment_rate_unemployed_pct, 3)}
          unit="%"
        />
      </div>

      <div className="h-[420px]">
        <RooftopMap geojson={geojson} cityCode={cityCode} metric="labor" />
      </div>

      <RooftopTable
        rows={rows}
        columns={[
          { key: "id", label: "ID" },
          { key: "commune_name", label: "Commune" },
          { key: "area", label: "Area (m²)", numeric: true },
          { key: "technique", label: "Technique" },
          { key: "social.labor_person_m2", label: "Labor / m²", numeric: true, digits: 6 },
          { key: "social.labor_person_total", label: "Labor (total)", numeric: true, digits: 2 },
          { key: "social.total_labor_cost", label: "Labor cost (MAD)", numeric: true, digits: 0 },
          { key: "social.accessibility_m2_per_person", label: "Accessibility (m²/p)", numeric: true, digits: 1 },
        ]}
      />
    </div>
  );
}

function fmt(v, d = 0) {
  if (v == null) return "—";
  return Number(v).toLocaleString(undefined, { maximumFractionDigits: d });
}
