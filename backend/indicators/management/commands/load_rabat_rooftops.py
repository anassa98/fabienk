"""
Load the bundled Rabat rooftop shapefile into Postgres.

The shapefile is in EPSG:32629 (UTM Zone 29N) and contains ~29k polygons across
six communes. By default we load a sample of 500 polygons (so the dashboard
stays responsive); pass --limit=0 to load everything.

Usage:
    python manage.py load_rabat_rooftops [--limit 500] [--seed 42] [--skip-pipeline]
"""
import random
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from indicators.models import City, Commune, Rooftop
from indicators.pipeline import run_full_pipeline


DEFAULT_SHAPEFILE = Path(settings.BASE_DIR) / "rabat_buildings_rooftops_suitable_1.shp"

CITY_CODE = "RAB"
CITY_NAME = "Rabat"
RABAT_POPULATION = 577_827
RABAT_UNEMPLOYED = 98_230


def _technique_for_fclass(fclass, rng):
    if fclass == "industrial":
        return "soilless"
    if fclass == "commercial":
        return rng.choice(["soilbased", "soilless"])
    return "soilbased"


def _system_for_fclass(fclass, rng):
    if fclass == "industrial":
        return "multiculture"
    return rng.choice(["monoculture", "multiculture"])


class Command(BaseCommand):
    help = "Load Rabat rooftops from the bundled shapefile into Postgres."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=500,
                            help="Max rooftops to load (0 = no limit, default 500).")
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--skip-pipeline", action="store_true",
                            help="Skip running the indicator pipeline after load.")
        parser.add_argument("--shapefile", default=str(DEFAULT_SHAPEFILE))

    @transaction.atomic
    def handle(self, *args, **opts):
        try:
            from pyogrio.raw import read as pyogrio_read
        except ImportError as exc:
            raise CommandError(
                "pyogrio is required. Install it with: pip install pyogrio"
            ) from exc

        path = opts["shapefile"]
        if not Path(path).exists():
            raise CommandError(f"Shapefile not found: {path}")

        limit = opts["limit"] or None
        rng = random.Random(opts["seed"])

        self.stdout.write(f"Reading {path}...")
        meta, _fids, geometries, field_data = pyogrio_read(path, max_features=limit)
        fields = list(meta["fields"])
        idx = {name: i for i, name in enumerate(fields)}
        n_features = len(geometries)
        self.stdout.write(f"  {n_features:,} features loaded.")

        self.stdout.write("Reprojecting geometries (UTM 29N -> WGS84)...")
        wgs_polys = []
        for wkb in geometries:
            g = GEOSGeometry(memoryview(wkb), srid=32629)
            g.transform(4326)
            wgs_polys.append(g)

        all_x = [p.centroid.x for p in wgs_polys]
        all_y = [p.centroid.y for p in wgs_polys]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        bbox = Polygon((
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y),
            (min_x, min_y),
        ))

        self.stdout.write(f"Upserting city {CITY_NAME}...")
        city, _ = City.objects.update_or_create(
            city_code=CITY_CODE,
            defaults={
                "name": CITY_NAME,
                "population": RABAT_POPULATION,
                "unemployed_population": RABAT_UNEMPLOYED,
                "rooftop_area_m2": int(sum(field_data[idx["AREA"]])),
                "ground_area_m2": 60_000_000,
                "annee_creation": 2025,
                "horizon_years": 20,
                "geometry": MultiPolygon(bbox),
            },
        )

        commune_names = sorted(set(field_data[idx["Commune"]]))
        self.stdout.write(f"Upserting {len(commune_names)} communes...")
        commune_objs = {}
        for cname in commune_names:
            code = f"{CITY_CODE}-{cname[:10].replace(' ', '_').upper()}"
            commune, _ = Commune.objects.update_or_create(
                commune_code=code,
                defaults={"name": cname, "city": city},
            )
            commune_objs[cname] = commune

        self.stdout.write("Clearing previous Rabat rooftops...")
        Rooftop.objects.filter(commune__city=city).delete()

        self.stdout.write(f"Creating {n_features:,} rooftops...")
        commune_col = field_data[idx["Commune"]]
        fclass_col = field_data[idx["FCLASS"]]
        area_col = field_data[idx["AREA"]]
        pop_col = field_data[idx["POPULATION"]]

        rooftops = []
        for i, geom in enumerate(wgs_polys):
            cname = commune_col[i]
            fclass = fclass_col[i]
            area_val = float(area_col[i] or 0)
            pop_val = int(pop_col[i] or 0)
            technique = _technique_for_fclass(fclass, rng)
            system = _system_for_fclass(fclass, rng)
            rooftops.append(Rooftop(
                commune=commune_objs[cname],
                area=Decimal(str(round(area_val, 2))),
                perimeter=Decimal(str(round(4 * (area_val ** 0.5), 2))),
                population=pop_val,
                ratio_a_p=Decimal("4"),
                technique=technique,
                system=system,
                geometry=geom if isinstance(geom, Polygon) else geom,
            ))

        Rooftop.objects.bulk_create(rooftops, batch_size=2000)
        self.stdout.write(self.style.SUCCESS(f"  Inserted {len(rooftops):,} rooftops."))

        if opts["skip_pipeline"]:
            self.stdout.write("Skipping pipeline (--skip-pipeline).")
            return

        self.stdout.write("Running pipeline (productivity / social / environmental / financial)...")
        run_full_pipeline(
            city,
            price_per_kg=Decimal("12"),
            capex_per_m2=Decimal("500"),
            opex_per_m2=Decimal("20"),
            vla=Decimal("100000"),
            zone="urbaine",
        )
        self.stdout.write(self.style.SUCCESS("Pipeline complete."))
