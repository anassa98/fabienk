import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";
import CitySelector from "../components/CitySelector";
import RooftopMap from "../components/RooftopMap";
import RooftopTable from "../components/RooftopTable";
import { useCityRooftops, useCityRooftopsTable, useCityStats } from "../hooks/useCityData";

export default function ProductivityPage({ cityCode, setCityCode }) {
  const { data: geojson } = useCityRooftops(cityCode);
  const { data: rows = [] } = useCityRooftopsTable(cityCode);
  const { data: stats } = useCityStats(cityCode);

  const chartData = rows.map((r) => ({
    name: `R${r.id}`,
    yield: Number(r.productivity?.total_yield ?? 0),
    ssr: Number(r.productivity?.ssr ?? 0),
  }));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Productivity Indicators</h1>
        <CitySelector value={cityCode} onChange={setCityCode} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <KPI label="Total yield (kg)" value={stats?.total_yield_kg} />
        <KPI label="Food demand (kg)" value={stats?.food_demand_kg} />
        <KPI label="SSR (city)" value={stats?.ssr_city_pct} unit="%" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="h-[400px]">
          <RooftopMap geojson={geojson} cityCode={cityCode} metric="yield" />
        </div>
        <div className="bg-white rounded-md border border-slate-200 shadow-sm p-3 h-[400px]">
          <div className="text-sm font-semibold mb-2">Yield by rooftop</div>
          <ResponsiveContainer width="100%" height="92%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="yield" fill="#16a34a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <RooftopTable
        rows={rows}
        columns={[
          { key: "id", label: "ID" },
          { key: "commune_name", label: "Commune" },
          { key: "area", label: "Area (m²)", numeric: true },
          { key: "technique", label: "Technique" },
          { key: "system", label: "System" },
          { key: "productivity.total_yield", label: "Yield (kg)", numeric: true },
          { key: "productivity.yield_per_capita", label: "Yield/cap", numeric: true, digits: 3 },
          { key: "productivity.ssr", label: "SSR (%)", numeric: true, digits: 2 },
        ]}
      />
    </div>
  );
}

function KPI({ label, value, unit }) {
  const num = value == null ? "—" : Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
  return (
    <div className="bg-white rounded-md border border-slate-200 shadow-sm px-4 py-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-xl font-semibold text-slate-800">
        {num} {unit && <span className="text-sm text-slate-500">{unit}</span>}
      </div>
    </div>
  );
}
