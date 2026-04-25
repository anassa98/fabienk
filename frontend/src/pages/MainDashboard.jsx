import { useState } from "react";
import CitySelector from "../components/CitySelector";
import RooftopMap from "../components/RooftopMap";
import StatPanel from "../components/StatPanel";
import { useCityRooftops } from "../hooks/useCityData";

export default function MainDashboard({ cityCode, setCityCode }) {
  const [metric, setMetric] = useState("yield");
  const { data: geojson, isLoading } = useCityRooftops(cityCode);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold text-slate-800">Main Dashboard</h1>
        <div className="flex items-center gap-3">
          <CitySelector value={cityCode} onChange={setCityCode} />
          <select
            className="border border-slate-300 rounded px-2 py-1.5 text-sm bg-white"
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
          >
            <option value="yield">Color: Total yield</option>
            <option value="ssr">Color: SSR</option>
            <option value="labor">Color: Labor (persons)</option>
            <option value="co2_balance">Color: Net CO₂ balance</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 h-[480px]">
          {isLoading ? (
            <div className="bg-white border rounded-md h-full flex items-center justify-center text-slate-500">
              Loading map…
            </div>
          ) : (
            <RooftopMap geojson={geojson} cityCode={cityCode} metric={metric} />
          )}
        </div>
        <div>
          <StatPanel cityCode={cityCode} />
        </div>
      </div>
    </div>
  );
}
