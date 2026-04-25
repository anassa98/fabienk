import StatCard from "./StatCard";
import { useCityStats } from "../hooks/useCityData";

const fmtNum = (v, digits = 0) => {
  if (v == null) return "—";
  const n = Number(v);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
};

export default function StatPanel({ cityCode }) {
  const { data: stats, isLoading } = useCityStats(cityCode);

  if (!cityCode)
    return (
      <div className="text-sm text-slate-500 italic">
        Select a city to load aggregate statistics.
      </div>
    );
  if (isLoading) return <div className="text-sm text-slate-500">Loading stats…</div>;
  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      <StatCard label="Population" value={fmtNum(stats.population)} />
      <StatCard label="Rooftops" value={fmtNum(stats.rooftop_count)} />
      <StatCard label="Total Area" value={fmtNum(stats.total_area_m2, 0)} unit="m²" />
      <StatCard label="Total Yield" value={fmtNum(stats.total_yield_kg, 0)} unit="kg" />
      <StatCard label="Food Demand" value={fmtNum(stats.food_demand_kg, 0)} unit="kg" />
      <StatCard label="SSR (city)" value={fmtNum(stats.ssr_city_pct, 2)} unit="%" />
      <StatCard label="Farmers" value={fmtNum(stats.farmers)} />
      <StatCard
        label="Empl. rate"
        value={fmtNum(stats.employment_rate_total_pct, 3)}
        unit="%"
      />
      <StatCard
        label="CO₂ seq."
        value={fmtNum(stats.total_co2_seq_t, 2)}
        unit="t"
      />
      <StatCard
        label="CO₂ emis."
        value={fmtNum(stats.total_co2_emis_t, 2)}
        unit="t"
      />
      <StatCard
        label="Net CO₂"
        value={fmtNum(stats.net_co2_balance_t, 2)}
        unit="t"
      />
    </div>
  );
}
