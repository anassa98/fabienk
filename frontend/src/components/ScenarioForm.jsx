import { useState } from "react";
import { useRunScenario } from "../hooks/useScenario";

export default function ScenarioForm({ cityCode, onResult }) {
  const [horizon, setHorizon] = useState(20);
  const [discountRate, setDiscountRate] = useState("0.08");
  const [pricePerKg, setPricePerKg] = useState("12");
  const [capexPerM2, setCapexPerM2] = useState("500");
  const [opexPerM2, setOpexPerM2] = useState("20");
  const [vla, setVla] = useState("100000");
  const [zone, setZone] = useState("urbaine");

  const mutation = useRunScenario();

  const submit = (e) => {
    e.preventDefault();
    if (!cityCode) return;
    mutation.mutate(
      {
        city_code: cityCode,
        horizon_years: Number(horizon),
        discount_rate: Number(discountRate),
        price_per_kg: Number(pricePerKg),
        capex_per_m2: Number(capexPerM2),
        opex_per_m2: Number(opexPerM2),
        vla: Number(vla),
        zone,
      },
      { onSuccess: (data) => onResult && onResult(data) }
    );
  };

  return (
    <form
      onSubmit={submit}
      className="bg-white rounded-md border border-slate-200 p-4 shadow-sm space-y-3"
    >
      <div className="text-sm font-semibold text-slate-700">Scenario simulator</div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <Field label="Horizon (years)" value={horizon} onChange={setHorizon} type="number" />
        <Field label="Discount rate" value={discountRate} onChange={setDiscountRate} step="0.01" />
        <Field label="Price (MAD/kg)" value={pricePerKg} onChange={setPricePerKg} />
        <Field label="CAPEX (MAD/m²)" value={capexPerM2} onChange={setCapexPerM2} />
        <Field label="OPEX (MAD/m²/yr)" value={opexPerM2} onChange={setOpexPerM2} />
        <Field label="VLA (MAD)" value={vla} onChange={setVla} />
        <div>
          <label className="block text-xs text-slate-500 mb-1">Zone</label>
          <select
            className="w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
            value={zone}
            onChange={(e) => setZone(e.target.value)}
          >
            <option value="urbaine">Urbaine</option>
            <option value="periurbaine">Périurbaine</option>
          </select>
        </div>
      </div>
      <div className="flex items-center justify-between pt-2">
        <button
          type="submit"
          disabled={!cityCode || mutation.isPending}
          className="bg-upa-primary text-white px-4 py-1.5 rounded text-sm disabled:opacity-50"
        >
          {mutation.isPending ? "Running…" : "Run scenario"}
        </button>
        {mutation.isError && (
          <span className="text-xs text-red-600">
            {mutation.error?.response?.data?.detail || "Failed."}
          </span>
        )}
        {mutation.isSuccess && (
          <span className="text-xs text-green-700">Done.</span>
        )}
      </div>
    </form>
  );
}

function Field({ label, value, onChange, type = "text", step }) {
  return (
    <div>
      <label className="block text-xs text-slate-500 mb-1">{label}</label>
      <input
        type={type}
        step={step}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border border-slate-300 rounded px-2 py-1.5 text-sm"
      />
    </div>
  );
}
