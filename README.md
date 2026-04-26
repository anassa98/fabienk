# UPA Framework — Urban-Periurban Agriculture Dashboard

PostgreSQL (PostGIS) + Django + React MVP for urban rooftop agriculture
indicators (productivity, social, environmental, economic, financial).

A real shapefile of **Rabat suitable rooftops** (29,198 polygons across 6
communes, EPSG:32629) is bundled and used as the live test data.

## Project layout

```
fabienk/
├── backend/                                   # Django + DRF + PostGIS
│   ├── upa_backend/                           # settings, URLs, WSGI
│   ├── indicators/                            # models, serializers, views, pipeline
│   │   └── management/commands/
│   │       ├── seed_demo.py                   # synthetic Casablanca + Marrakech
│   │       └── load_rabat_rooftops.py         # real Rabat shapefile loader
│   ├── rabat_buildings_rooftops_suitable_1.*  # shapefile (UTM 29N)
│   ├── Dockerfile                             # GDAL/GEOS/PROJ + gunicorn
│   ├── requirements.txt
│   └── .env.example
├── frontend/                                  # Vite + React + Tailwind
├── docker-compose.yml                         # local PostGIS
├── render.yaml                                # one-click backend deploy
├── vercel.json                                # frontend deploy config
└── README.md
```

## Local development

### 1. PostGIS

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo                # synthetic Casablanca + Marrakech
python manage.py load_rabat_rooftops      # real Rabat from shapefile (sample 500)
# Or load everything (~29k polygons; pipeline takes longer):
# python manage.py load_rabat_rooftops --limit 0
python manage.py createsuperuser
python manage.py runserver
```

API: `http://localhost:8000/api/` — Admin: `http://localhost:8000/admin/`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` → `localhost:8000`. Open `http://localhost:5173`.

## Deployment

This stack splits cleanly across two hosts:

| Piece | Host | Why |
|---|---|---|
| Frontend | **Vercel** | Static Vite build, zero-config |
| Backend + DB | **Render** | Native Docker, GDAL pre-installable, managed Postgres+PostGIS |

### Backend → Render

The repo includes `render.yaml` + `backend/Dockerfile`.

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New → Blueprint** → select the repo.
   Render reads `render.yaml`, provisions:
   - `upa-backend` web service (Docker, free tier)
   - `upa-postgres` Postgres database
3. After the Postgres DB is up, run **once** in the Render shell (or via the
   one-time job feature):
   ```bash
   psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS postgis;"
   ```
4. Run the migrations + seeds (Render shell on the web service):
   ```bash
   python manage.py migrate
   python manage.py seed_demo
   python manage.py load_rabat_rooftops
   python manage.py createsuperuser
   ```
5. Note the service URL, e.g. `https://upa-backend.onrender.com`.
6. In the Render dashboard, set on `upa-backend`:
   - `CORS_ALLOWED_ORIGINS=https://<your-vercel-domain>.vercel.app`
   - `CSRF_TRUSTED_ORIGINS=https://<your-vercel-domain>.vercel.app`

> Why not Vercel for the backend? Vercel's Python runtime is AWS-Lambda-based
> and does not bundle the GDAL/GEOS/PROJ native libs that
> `django.contrib.gis` and `rest_framework_gis` require. Render's Docker
> runtime gives us those out of the box.

### Frontend → Vercel

1. [vercel.com](https://vercel.com) → **Add New Project** → select the repo.
2. Vercel reads `vercel.json` (root dir, build command, output dir).
3. In **Project Settings → Environment Variables**, set:
   - `VITE_API_BASE_URL=https://upa-backend.onrender.com/api`
4. Deploy. Subsequent pushes to the configured branch auto-deploy.

### Alternative: PostGIS on Neon

Neon's free tier supports PostGIS. To use it instead of Render's Postgres:

1. Create a Neon project, run `CREATE EXTENSION postgis;` in the SQL editor.
2. Copy the connection string (use the pooled `?sslmode=require` URL).
3. In Render's `upa-backend` service, replace the `DATABASE_URL` env var
   value with the Neon connection string. Remove the `databases:` block from
   `render.yaml` if you want a Neon-only setup.

## API surface

| Method | Path | Purpose |
|---|---|---|
| GET  | `/healthz` | Health check |
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

## Shapefile loader

`load_rabat_rooftops` reads the bundled
`backend/rabat_buildings_rooftops_suitable_1.shp`, reprojects each polygon
from EPSG:32629 (UTM Zone 29N) to EPSG:4326 (WGS84), creates the City
"Rabat" + 6 Communes (Agdal Riyad, Souissi, Yacoub El Mansour, Hassan,
El Youssoufia, Touarga), then bulk-inserts the rooftops. After loading, it
runs the full indicator + financial pipeline.

Flags:
- `--limit N` — load at most N features (default 500). `--limit 0` = all.
- `--seed N` — RNG seed for technique/system assignment.
- `--skip-pipeline` — load without running the indicator chain.
- `--shapefile PATH` — override the default shapefile path.
