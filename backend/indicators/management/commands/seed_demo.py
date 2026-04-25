"""
Seed the database with a small demo dataset (one city, one commune, a handful
of rooftops) and run the full pipeline so the dashboard has something to show.

Usage:
    python manage.py seed_demo
"""
from decimal import Decimal
import random

from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand

from indicators.models import City, Commune, Rooftop
from indicators.pipeline import run_full_pipeline


CITIES = [
    {
        "city_code": "CAS",
        "name": "Casablanca",
        "population": 3_359_818,
        "unemployed_population": 638_365,
        "rooftop_area_m2": 50_000_000,
        "ground_area_m2": 200_000_000,
        "center": (-7.5898, 33.5731),
        "annee_creation": 2025,
    },
    {
        "city_code": "RAB",
        "name": "Rabat",
        "population": 577_827,
        "unemployed_population": 98_230,
        "rooftop_area_m2": 18_000_000,
        "ground_area_m2": 60_000_000,
        "center": (-6.8498, 34.0209),
        "annee_creation": 2025,
    },
    {
        "city_code": "MRK",
        "name": "Marrakech",
        "population": 928_850,
        "unemployed_population": 139_328,
        "rooftop_area_m2": 22_000_000,
        "ground_area_m2": 80_000_000,
        "center": (-7.9811, 31.6295),
        "annee_creation": 2025,
    },
]


def _square_polygon(lon, lat, half_size_deg):
    """Build a small square polygon centered at (lon, lat)."""
    return Polygon(((
        (lon - half_size_deg, lat - half_size_deg),
        (lon + half_size_deg, lat - half_size_deg),
        (lon + half_size_deg, lat + half_size_deg),
        (lon - half_size_deg, lat + half_size_deg),
        (lon - half_size_deg, lat - half_size_deg),
    ),))


class Command(BaseCommand):
    help = "Seed demo cities, communes, rooftops and run the pipeline."

    def add_arguments(self, parser):
        parser.add_argument("--rooftops", type=int, default=15,
                            help="Number of rooftops to create per city (default 15)")
        parser.add_argument("--seed", type=int, default=42,
                            help="Random seed (default 42)")

    def handle(self, *args, **options):
        rng = random.Random(options["seed"])
        n_per_city = options["rooftops"]

        for city_def in CITIES:
            self.stdout.write(f"Seeding {city_def['name']}...")
            lon, lat = city_def["center"]
            city_geom = MultiPolygon(_square_polygon(lon, lat, 0.10))

            city, _ = City.objects.update_or_create(
                city_code=city_def["city_code"],
                defaults={
                    "name": city_def["name"],
                    "population": city_def["population"],
                    "unemployed_population": city_def["unemployed_population"],
                    "rooftop_area_m2": city_def["rooftop_area_m2"],
                    "ground_area_m2": city_def["ground_area_m2"],
                    "annee_creation": city_def["annee_creation"],
                    "horizon_years": 20,
                    "geometry": city_geom,
                },
            )

            commune_code = f"{city.city_code}-C01"
            commune, _ = Commune.objects.update_or_create(
                commune_code=commune_code,
                defaults={
                    "name": f"{city.name} Centre",
                    "city": city,
                    "geometry": MultiPolygon(_square_polygon(lon, lat, 0.05)),
                },
            )

            Rooftop.objects.filter(commune=commune).delete()

            for i in range(n_per_city):
                rlon = lon + rng.uniform(-0.04, 0.04)
                rlat = lat + rng.uniform(-0.04, 0.04)
                size = rng.uniform(0.0008, 0.0025)
                area = Decimal(str(round(rng.uniform(150, 500), 2)))
                technique = rng.choice(["soilbased", "soilless"])
                system = rng.choice(["monoculture", "multiculture"])
                Rooftop.objects.create(
                    commune=commune,
                    area=area,
                    perimeter=area / Decimal("4"),
                    population=rng.randint(20, 250),
                    ratio_a_p=Decimal("4"),
                    technique=technique,
                    system=system,
                    geometry=_square_polygon(rlon, rlat, size),
                )

            self.stdout.write("  Running pipeline...")
            run_full_pipeline(
                city,
                price_per_kg=Decimal("12"),
                capex_per_m2=Decimal("500"),
                opex_per_m2=Decimal("20"),
                vla=Decimal("100000"),
                zone="urbaine",
            )
            self.stdout.write(self.style.SUCCESS(f"  Done: {city.name}"))

        self.stdout.write(self.style.SUCCESS("Demo seeding complete."))
