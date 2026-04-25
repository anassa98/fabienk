import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", icon: "🗺️" },
  { to: "/productivity", label: "Productivity", icon: "🌱" },
  { to: "/social", label: "Social", icon: "👥" },
  { to: "/environmental", label: "Environmental", icon: "🌍" },
  { to: "/economic", label: "Economic", icon: "💰" },
  { to: "/financial", label: "Financial", icon: "📊" },
];

export default function Sidebar() {
  return (
    <aside className="w-56 bg-upa-dark text-slate-100 flex flex-col">
      <div className="px-5 py-5 border-b border-slate-700">
        <h1 className="text-lg font-bold leading-tight">UPA Framework</h1>
        <p className="text-xs text-slate-400">Urban Agriculture Dashboard</p>
      </div>
      <nav className="flex-1 py-3">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-2.5 text-sm transition-colors ${
                isActive
                  ? "bg-upa-primary text-white"
                  : "text-slate-300 hover:bg-slate-800"
              }`
            }
          >
            <span>{l.icon}</span>
            <span>{l.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="px-5 py-3 text-xs text-slate-500 border-t border-slate-700">
        v0.1.0 — MVP
      </div>
    </aside>
  );
}
