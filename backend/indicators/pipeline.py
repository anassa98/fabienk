"""
Pipeline orchestrator: runs the full UPA Framework computation chain for a city.
"""
from decimal import Decimal

from django.db import transaction

from .models import (
    City,
    EconomicBase,
    EnvironmentalIndicators,
    FinancialPerformance,
    ProductivityIndicators,
    Rooftop,
    SocialIndicators,
    Taxation,
)


@transaction.atomic
def compute_rooftop_indicators(rooftop: Rooftop, tier_k: int = 2):
    """Compute productivity, social, and environmental indicators for one rooftop."""
    prod, _ = ProductivityIndicators.objects.get_or_create(rooftop=rooftop)
    prod.calculate_all(tier_k=tier_k)
    prod.save()

    social, _ = SocialIndicators.objects.get_or_create(rooftop=rooftop)
    social.calculate_all()
    social.save()

    env, _ = EnvironmentalIndicators.objects.get_or_create(rooftop=rooftop)
    env.compute()
    env.save()

    return prod, social, env


@transaction.atomic
def run_full_pipeline(
    city: City,
    *,
    horizon_years: int = None,
    discount_rate: Decimal = None,
    price_per_kg: Decimal = Decimal("10"),
    capex_per_m2: Decimal = Decimal("500"),
    opex_per_m2: Decimal = Decimal("20"),
    vla: Decimal = Decimal("0"),
    zone: str = "urbaine",
    achats_non_exoneres_ht: Decimal = Decimal("0"),
    tier_k: int = 2,
):
    """
    Run the full computation chain for a city:
      1. Per-rooftop indicators (productivity, social, environmental)
      2. Per-year economic base + taxation across the investment horizon
      3. City-level aggregates
      4. Financial performance (NPV, IRR, BCR, payback)
    """
    if horizon_years is not None:
        city.horizon_years = horizon_years

    for rooftop in city.rooftops:
        compute_rooftop_indicators(rooftop, tier_k=tier_k)

    total_area = sum((r.area for r in city.rooftops), Decimal("0"))
    capex_total = total_area * capex_per_m2
    opex_total = total_area * opex_per_m2

    start = city.annee_creation
    end = start + city.horizon_years
    for year in range(start, end + 1):
        eb, _ = EconomicBase.objects.get_or_create(city=city, year=year)
        eb.capex = capex_total if year == start else Decimal("0")
        eb.opex = opex_total if year > start else Decimal("0")
        eb.calculate_gross_revenue(price_per_kg)
        eb.calculate_pretax_net()
        eb.save()

        tax, _ = Taxation.objects.get_or_create(economic_base=eb)
        tax.calculate_all(
            vla=vla,
            zone=zone,
            achats_non_exoneres_ht=achats_non_exoneres_ht,
        )
        tax.save()

    city.calculate_all()
    city.save()

    fp, _ = FinancialPerformance.objects.get_or_create(city=city)
    if discount_rate is not None:
        fp.discount_rate = discount_rate
    fp.calculate_all()
    fp.save()

    return fp
