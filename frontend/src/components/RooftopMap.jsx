import { useEffect, useMemo, useRef } from "react";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import L from "leaflet";

// Default Leaflet marker icons fail with bundlers — patch them.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const CITY_CENTERS = {
  CAS: [33.5731, -7.5898],
  RAB: [34.0209, -6.8498],
  MRK: [31.6295, -7.9811],
};

function colorScale(value, min, max) {
  if (max === min) return "#16a34a";
  const t = Math.min(1, Math.max(0, (value - min) / (max - min)));
  // red (low) -> yellow (mid) -> green (high)
  const r = Math.round(220 + (22 - 220) * t);
  const g = Math.round(80 + (163 - 80) * t);
  const b = Math.round(80 + (74 - 80) * t);
  return `rgb(${r},${g},${b})`;
}

function FitBounds({ data }) {
  const map = useMap();
  useEffect(() => {
    if (!data?.features?.length) return;
    try {
      const layer = L.geoJSON(data);
      const bounds = layer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [20, 20] });
      }
    } catch (e) {
      // ignore
    }
  }, [data, map]);
  return null;
}

export default function RooftopMap({
  geojson,
  cityCode,
  metric = "yield",
  onSelectFeature,
}) {
  const ref = useRef();
  const center = CITY_CENTERS[cityCode] || [31.5, -7.5];

  const { min, max } = useMemo(() => {
    if (!geojson?.features?.length) return { min: 0, max: 1 };
    const values = geojson.features
      .map((f) => extractMetric(f, metric))
      .filter((v) => v != null && Number.isFinite(v));
    if (!values.length) return { min: 0, max: 1 };
    return { min: Math.min(...values), max: Math.max(...values) };
  }, [geojson, metric]);

  const style = (feature) => {
    const v = extractMetric(feature, metric);
    return {
      color: "#1e293b",
      weight: 1,
      fillColor: v == null ? "#94a3b8" : colorScale(v, min, max),
      fillOpacity: 0.7,
    };
  };

  const onEachFeature = (feature, layer) => {
    const p = feature.properties || {};
    const yieldVal = p.productivity?.total_yield ?? "—";
    const ssr = p.productivity?.ssr ?? "—";
    layer.bindPopup(
      `<div class="text-sm">
        <div><strong>Rooftop ${feature.id}</strong></div>
        <div>Commune: ${p.commune_name ?? "—"}</div>
        <div>Area: ${p.area} m²</div>
        <div>Technique: ${p.technique}</div>
        <div>System: ${p.system}</div>
        <div>Yield: ${yieldVal} kg</div>
        <div>SSR: ${ssr}%</div>
      </div>`
    );
    layer.on({
      click: () => onSelectFeature && onSelectFeature(feature),
    });
  };

  return (
    <MapContainer
      ref={ref}
      center={center}
      zoom={12}
      className="rounded-md shadow"
      style={{ height: "100%", minHeight: 380 }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {geojson?.features?.length > 0 && (
        <>
          <GeoJSON
            key={`${cityCode}-${metric}`}
            data={geojson}
            style={style}
            onEachFeature={onEachFeature}
          />
          <FitBounds data={geojson} />
        </>
      )}
    </MapContainer>
  );
}

function extractMetric(feature, metric) {
  const p = feature.properties || {};
  const num = (x) => (x == null ? null : Number(x));
  switch (metric) {
    case "yield":
      return num(p.productivity?.total_yield);
    case "ssr":
      return num(p.productivity?.ssr);
    case "labor":
      return num(p.social?.labor_person_total);
    case "labor_cost":
      return num(p.social?.total_labor_cost);
    case "co2_seq":
      return num(p.environmental?.co2_seq_t);
    case "co2_emis":
      return num(p.environmental?.co2_emissions_t);
    case "co2_balance":
      return num(p.environmental?.net_co2_balance_t);
    default:
      return null;
  }
}
