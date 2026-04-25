const fmt = (v, digits = 2) => {
  if (v == null) return "—";
  const n = Number(v);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
};

export default function RooftopTable({ rows, columns }) {
  if (!rows?.length)
    return <div className="text-sm text-slate-500 italic">No rooftops.</div>;

  return (
    <div className="overflow-x-auto bg-white rounded-md border border-slate-200 shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-100 text-slate-700">
          <tr>
            {columns.map((c) => (
              <th key={c.key} className="text-left px-3 py-2 font-medium">
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.id ?? i} className="border-t border-slate-100 hover:bg-slate-50">
              {columns.map((c) => (
                <td key={c.key} className="px-3 py-2 text-slate-700">
                  {c.render
                    ? c.render(r)
                    : c.numeric
                    ? fmt(getPath(r, c.key), c.digits ?? 2)
                    : getPath(r, c.key) ?? "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function getPath(obj, path) {
  return path.split(".").reduce((acc, k) => (acc == null ? acc : acc[k]), obj);
}
