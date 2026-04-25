# UPA Framework — Urban-Periurban Agriculture Dashboard

PostgreSQL (PostGIS) + Django + React MVP that implements the class diagram for
urban rooftop agriculture indicators (productivity, social, environmental,
economic, financial).

## Project layout

```
fabienk/
├── backend/              # Django + DRF + PostGIS
│   ├── upa_backend/      # Project settings, URLs, WSGI
│   └── indicators/       # App: models, serializers, views, pipeline, admin
├── frontend/             # Vite + React + Tailwind + Leaflet + Recharts
│   └── src/
│       ├── pages/        # MainDashboard, Productivity, Social, Environmental, Economic, Financial
│       ├── components/   # Sidebar, Map, CitySelector, StatPanel, ScenarioForm, ...
│       ├── hooks/        # TanStack Query hooks
│       └── api/          # Axios client
├── docker-compose.yml    # PostGIS service
└── .gitignore
```

## Quick start

### 1. PostGIS (via Docker)

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # adjust if needed
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

API available at `http://localhost:8000/api/`. Admin at `http://localhost:8000/admin/`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to Django.

## API surface

| Method | Path | Purpose |
|---|---|---|
| GET  | `/api/cities/` | List cities |
| GET  | `/api/cities/<code>/` | City detail |
| GET  | `/api/cities/<code>/rooftops/` | Rooftops as GeoJSON |
| GET  | `/api/cities/<code>/rooftops-table/` | Rooftops as JSON table |
| GET  | `/api/cities/<code>/stats/` | City-level aggregate stats |
| GET  | `/api/cities/<code>/financial/` | Latest financial performance |
| GET  | `/api/rooftops/<id>/productivity/` | Per-rooftop productivity |
| GET  | `/api/rooftops/<id>/social/` | Per-rooftop social |
| GET  | `/api/rooftops/<id>/environmental/` | Per-rooftop environmental |
| POST | `/api/scenarios/` | Run the full pipeline for a city |

`POST /api/scenarios/` body:

```json
{
  "city_code": "CAS",
  "horizon_years": 20,
  "discount_rate": 0.08,
  "price_per_kg": 12,
  "capex_per_m2": 500,
  "opex_per_m2": 20,
  "vla": 100000,
  "zone": "urbaine",
  "tier_k": 2
}
```

## Development notes

- The Django pipeline (`indicators/pipeline.py`) chains:
  1. Productivity / Social / Environmental indicators per rooftop.
  2. Per-year `EconomicBase` and `Taxation` rows over the investment horizon.
  3. City-level aggregates.
  4. `FinancialPerformance` (NPV, IRR, BCR, ROR, payback).
- For local quick iteration without PostGIS, set `DB_ENGINE=sqlite` in
  `backend/.env` (but you lose geometry support).
- The seed command (`seed_demo`) creates Casablanca, Rabat, Marrakech with
  one commune and 15 random rooftops each, then runs the pipeline.
