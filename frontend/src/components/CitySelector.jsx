import { useCities } from "../hooks/useCityData";

export default function CitySelector({ value, onChange }) {
  const { data, isLoading, isError } = useCities();
  const cities = data?.results ?? data ?? [];

  if (isLoading) return <span className="text-sm text-slate-500">Loading cities…</span>;
  if (isError) return <span className="text-sm text-red-600">Failed to load cities.</span>;

  return (
    <div className="flex items-center gap-2">
      <label className="text-sm font-medium text-slate-700">City:</label>
      <select
        className="border border-slate-300 rounded px-3 py-1.5 text-sm bg-white"
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="" disabled>
          Select a city…
        </option>
        {cities.map((c) => (
          <option key={c.city_code} value={c.city_code}>
            {c.name}
          </option>
        ))}
      </select>
    </div>
  );
}
