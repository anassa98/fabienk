import { useState } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import CitySelector from "../components/CitySelector";
import ScenarioForm from "../components/ScenarioForm";
import StatCard from "../components/StatCard";
import { useCityFinancial } from "../hooks/useCityData";

export default function FinancialPage({ cityCode, setCityCode }) {
  const [scenario, setScenario] = useState(null);
  const { data: existing, isError } = useCityFinancial(cityCode);
  const data = scenario || existing;

  const fp = data?.financial;
  const cashFlows = (data?.cash_flows ?? []).map((v) => Number(v));
  const startYear = data?.economic_bases?.[0]?.year ?? 0;
  const cumulative = [];
  cashFlows.reduce((acc, v, i) => {
    const c = acc + v;
    cumulative.push({ year: startYear + i, cashflow: v, cumulative: c });
    return c;
  }, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Financial Performance</h1>
        <CitySelector value={cityCode} onChange={setCityCode} />
      </div>

      <ScenarioForm cityCode={cityCode} onResult={setScenario} />

      {!fp && isError && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm rounded-md p-3">
          No scenario has been run yet for this city. Run one above.
        </div>
      )}

      {fp && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <StatCard label="NPV (MAD)" value={fmt(fp.npv_mad)} />
            <StatCard label="IRR" value={fmt(fp.irr_pct, 2)} unit="%" />
            <StatCard label="BCR" value={fmt(fp.bcr, 3)} />
            <StatCard label="ROR" value={fmt(fp.ror_pct, 2)} unit="%" />
            <StatCard label="Discounted ROR" value={fmt(fp.discounted_ror_pct, 2)} unit="%" />
            <StatCard label="Payback (years)" value={fp.payback_years ?? "—"} />
            <StatCard
              label="Discounted payback"
              value={fp.payback_discounted_years ?? "—"}
              unit="yrs"
            />
            <StatCard label="Discount rate" value={fmt(fp.discount_rate, 4)} />
          </div>

          <div className="bg-white rounded-md border border-slate-200 shadow-sm p-3 h-[400px]">
            <div className="text-sm font-semibold mb-2">
              Cash flow & cumulative cash flow
            </div>
            <ResponsiveContainer width="100%" height="92%">
              <AreaChart data={cumulative}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <ReferenceLine y={0} stroke="#475569" />
                <Area
                  type="monotone"
                  dataKey="cashflow"
                  stroke="#0ea5e9"
                  fill="#bae6fd"
                  name="Cash flow"
                />
                <Area
                  type="monotone"
                  dataKey="cumulative"
                  stroke="#16a34a"
                  fill="#bbf7d0"
                  name="Cumulative"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}

function fmt(v, d = 0) {
  if (v == null) return "—";
  const n = Number(v);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: d });
}
