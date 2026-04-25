import { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import CitySelector from "../components/CitySelector";
import ScenarioForm from "../components/ScenarioForm";
import StatCard from "../components/StatCard";
import { useCityFinancial } from "../hooks/useCityData";

export default function EconomicPage({ cityCode, setCityCode }) {
  const [scenario, setScenario] = useState(null);
  const { data: existing } = useCityFinancial(cityCode);
  const data = scenario || existing;
  const bases = data?.economic_bases ?? [];
  const cashFlows = data?.cash_flows ?? [];

  const chartData = bases.map((eb, i) => ({
    year: eb.year,
    revenue: Number(eb.gross_revenue),
    pretax: Number(eb.pretax_net),
    posttax: Number(eb.taxation?.posttax_net ?? eb.pretax_net),
    cashflow: Number(cashFlows[i] ?? 0),
  }));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Economic Indicators</h1>
        <CitySelector value={cityCode} onChange={setCityCode} />
      </div>

      <ScenarioForm cityCode={cityCode} onResult={setScenario} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-md border border-slate-200 shadow-sm p-3 h-[380px]">
          <div className="text-sm font-semibold mb-2">Revenue & profit over horizon</div>
          <ResponsiveContainer width="100%" height="92%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="revenue" stroke="#16a34a" />
              <Line type="monotone" dataKey="pretax" stroke="#0ea5e9" />
              <Line type="monotone" dataKey="posttax" stroke="#f59e0b" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-3">
          {bases.length > 0 && (
            <div className="grid grid-cols-2 gap-3">
              <StatCard
                label="Year 0 CAPEX"
                value={fmt(bases[0]?.capex)}
                unit="MAD"
              />
              <StatCard
                label="Avg gross revenue"
                value={fmt(avg(bases.map((b) => Number(b.gross_revenue))))}
                unit="MAD/yr"
              />
              <StatCard
                label="Avg pre-tax net"
                value={fmt(avg(bases.map((b) => Number(b.pretax_net))))}
                unit="MAD/yr"
              />
              <StatCard
                label="Avg post-tax net"
                value={fmt(
                  avg(bases.map((b) => Number(b.taxation?.posttax_net ?? b.pretax_net)))
                )}
                unit="MAD/yr"
              />
            </div>
          )}
          <div className="bg-white rounded-md border border-slate-200 shadow-sm overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-100">
                <tr>
                  <th className="px-3 py-2 text-left">Year</th>
                  <th className="px-3 py-2 text-right">Revenue</th>
                  <th className="px-3 py-2 text-right">Pre-tax</th>
                  <th className="px-3 py-2 text-right">Post-tax</th>
                  <th className="px-3 py-2 text-right">Cash flow</th>
                </tr>
              </thead>
              <tbody>
                {bases.map((eb, i) => (
                  <tr key={eb.id} className="border-t border-slate-100">
                    <td className="px-3 py-1.5">{eb.year}</td>
                    <td className="px-3 py-1.5 text-right">{fmt(eb.gross_revenue)}</td>
                    <td className="px-3 py-1.5 text-right">{fmt(eb.pretax_net)}</td>
                    <td className="px-3 py-1.5 text-right">
                      {fmt(eb.taxation?.posttax_net ?? eb.pretax_net)}
                    </td>
                    <td className="px-3 py-1.5 text-right">{fmt(cashFlows[i])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function fmt(v, d = 0) {
  if (v == null) return "—";
  const n = Number(v);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: d });
}
function avg(arr) {
  if (!arr.length) return 0;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}
