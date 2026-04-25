from decimal import Decimal

from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import (
    City,
    Commune,
    EconomicBase,
    FinancialPerformance,
    Rooftop,
)
from .pipeline import run_full_pipeline
from .serializers import (
    CitySerializer,
    CommuneSerializer,
    EconomicBaseSerializer,
    FinancialPerformanceSerializer,
    RooftopGeoSerializer,
    RooftopListSerializer,
    ScenarioRequestSerializer,
)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all().order_by("name")
    serializer_class = CitySerializer
    lookup_field = "city_code"

    @action(detail=True, methods=["get"], url_path="rooftops")
    def rooftops(self, request, city_code=None):
        """List all rooftops for a city as GeoJSON FeatureCollection."""
        city = self.get_object()
        qs = (
            Rooftop.objects
            .filter(commune__city=city)
            .select_related("commune", "productivity_indicators",
                            "social_indicators", "environmental_indicators")
        )
        serializer = RooftopGeoSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="rooftops-table")
    def rooftops_table(self, request, city_code=None):
        """Tabular (non-Geo) listing — easier for tables/charts."""
        city = self.get_object()
        qs = (
            Rooftop.objects
            .filter(commune__city=city)
            .select_related("commune", "productivity_indicators",
                            "social_indicators", "environmental_indicators")
        )
        serializer = RooftopListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def stats(self, request, city_code=None):
        """City-level aggregate statistics."""
        city = self.get_object()
        rooftops = city.rooftops.select_related(
            "productivity_indicators", "social_indicators", "environmental_indicators"
        )

        total_yield = sum(
            (getattr(r, "productivity_indicators", None).total_yield
             for r in rooftops if hasattr(r, "productivity_indicators")),
            Decimal("0"),
        )
        total_labor = sum(
            (r.social_indicators.labor_person_total
             for r in rooftops if hasattr(r, "social_indicators")),
            Decimal("0"),
        )
        total_co2_seq = sum(
            (r.environmental_indicators.co2_seq_t
             for r in rooftops if hasattr(r, "environmental_indicators")),
            Decimal("0"),
        )
        total_co2_emis = sum(
            (r.environmental_indicators.co2_emissions_t
             for r in rooftops if hasattr(r, "environmental_indicators")),
            Decimal("0"),
        )

        return Response({
            "city_code": city.city_code,
            "name": city.name,
            "population": city.population,
            "rooftop_count": rooftops.count(),
            "total_area_m2": rooftops.aggregate(s=Sum("area"))["s"] or 0,
            "total_yield_kg": total_yield,
            "ssr_city_pct": city.ssr_city,
            "ssr_buildings_pct": city.ssr_buildings_based,
            "yield_per_capita_city": city.yield_per_capita_city,
            "food_demand_kg": city.food_demand,
            "farmers": city.farmers,
            "employment_rate_total_pct": city.employment_rate_total_pct,
            "employment_rate_unemployed_pct": city.employment_rate_unemployed_pct,
            "buildings_per_farmer": city.buildings_per_farmer,
            "total_labor_persons": total_labor,
            "total_co2_seq_t": total_co2_seq,
            "total_co2_emis_t": total_co2_emis,
            "net_co2_balance_t": total_co2_seq - total_co2_emis,
        })


class CommuneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Commune.objects.select_related("city").all()
    serializer_class = CommuneSerializer
    lookup_field = "commune_code"


class RooftopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rooftop.objects.select_related(
        "commune", "commune__city",
        "productivity_indicators", "social_indicators", "environmental_indicators",
    )
    serializer_class = RooftopListSerializer

    @action(detail=True, methods=["get"])
    def productivity(self, request, pk=None):
        rooftop = self.get_object()
        prod = getattr(rooftop, "productivity_indicators", None)
        if prod is None:
            return Response({"detail": "Indicators not yet computed."},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({
            "rooftop_id": rooftop.id,
            "area": rooftop.area,
            "population": rooftop.population,
            "technique": rooftop.technique,
            "system": rooftop.system,
            "total_yield": prod.total_yield,
            "yield_per_capita": prod.yield_per_capita,
            "food_demand": prod.food_demand,
            "ssr": prod.ssr,
        })

    @action(detail=True, methods=["get"])
    def social(self, request, pk=None):
        rooftop = self.get_object()
        social = getattr(rooftop, "social_indicators", None)
        if social is None:
            return Response({"detail": "Indicators not yet computed."},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({
            "rooftop_id": rooftop.id,
            "labor_person_m2": social.labor_person_m2,
            "labor_person_total": social.labor_person_total,
            "total_labor_cost": social.total_labor_cost,
            "accessibility_m2_per_person": social.accessibility_m2_per_person,
        })

    @action(detail=True, methods=["get"])
    def environmental(self, request, pk=None):
        rooftop = self.get_object()
        env = getattr(rooftop, "environmental_indicators", None)
        if env is None:
            return Response({"detail": "Indicators not yet computed."},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({
            "rooftop_id": rooftop.id,
            "crop_dry_matter_kg": env.crop_dry_matter_kg,
            "total_dry_biomass_kg": env.total_dry_biomass_kg,
            "carbon_content_kg": env.carbon_content_kg,
            "co2_seq_kg": env.co2_seq_kg,
            "co2_seq_t": env.co2_seq_t,
            "co2_emissions_kg": env.co2_emissions_kg,
            "co2_emissions_t": env.co2_emissions_t,
            "net_co2_balance_kg": env.net_co2_balance_kg,
            "net_co2_balance_t": env.net_co2_balance_t,
        })


@api_view(["POST"])
def run_scenario(request):
    """POST /api/scenarios/ — run the full pipeline for a city."""
    serializer = ScenarioRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    city = get_object_or_404(City, city_code=data["city_code"])
    fp = run_full_pipeline(
        city,
        horizon_years=data.get("horizon_years"),
        discount_rate=data.get("discount_rate"),
        price_per_kg=Decimal(str(data["price_per_kg"])),
        capex_per_m2=Decimal(str(data["capex_per_m2"])),
        opex_per_m2=Decimal(str(data["opex_per_m2"])),
        vla=Decimal(str(data["vla"])),
        zone=data["zone"],
        achats_non_exoneres_ht=Decimal(str(data["achats_non_exoneres_ht"])),
        tier_k=data["tier_k"],
    )

    bases = (
        EconomicBase.objects
        .filter(city=city)
        .select_related("taxation")
        .order_by("year")
    )
    cash_flows = fp._cash_flows()

    return Response({
        "city": CitySerializer(city).data,
        "financial": FinancialPerformanceSerializer(fp).data,
        "cash_flows": [str(cf) for cf in cash_flows],
        "economic_bases": EconomicBaseSerializer(bases, many=True).data,
    })


@api_view(["GET"])
def city_financial(request, city_code):
    """GET /api/cities/<code>/financial/ — return current financial performance."""
    city = get_object_or_404(City, city_code=city_code)
    fp = getattr(city, "financial_performance", None)
    if fp is None:
        return Response({"detail": "No scenario has been run yet."},
                        status=status.HTTP_404_NOT_FOUND)
    bases = city.economic_bases.select_related("taxation").order_by("year")
    return Response({
        "city": CitySerializer(city).data,
        "financial": FinancialPerformanceSerializer(fp).data,
        "cash_flows": [str(cf) for cf in fp._cash_flows()],
        "economic_bases": EconomicBaseSerializer(bases, many=True).data,
    })
