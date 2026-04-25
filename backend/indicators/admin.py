from django.contrib import admin
from django.contrib.gis import admin as gis_admin

from .models import (
    City,
    Commune,
    EconomicBase,
    EnvironmentalIndicators,
    FinancialPerformance,
    ProductivityIndicators,
    Rooftop,
    SocialIndicators,
    Taxation,
)


@admin.register(City)
class CityAdmin(gis_admin.GISModelAdmin):
    list_display = ("city_code", "name", "population", "annee_creation",
                    "horizon_years", "ssr_city", "farmers")
    search_fields = ("city_code", "name")


@admin.register(Commune)
class CommuneAdmin(gis_admin.GISModelAdmin):
    list_display = ("commune_code", "name", "city")
    list_filter = ("city",)
    search_fields = ("commune_code", "name")


@admin.register(Rooftop)
class RooftopAdmin(gis_admin.GISModelAdmin):
    list_display = ("id", "commune", "area", "population", "technique", "system")
    list_filter = ("technique", "system", "commune__city")
    search_fields = ("id", "commune__name")


@admin.register(ProductivityIndicators)
class ProductivityIndicatorsAdmin(admin.ModelAdmin):
    list_display = ("rooftop", "total_yield", "yield_per_capita", "ssr")


@admin.register(SocialIndicators)
class SocialIndicatorsAdmin(admin.ModelAdmin):
    list_display = ("rooftop", "labor_person_total", "total_labor_cost")


@admin.register(EnvironmentalIndicators)
class EnvironmentalIndicatorsAdmin(admin.ModelAdmin):
    list_display = ("rooftop", "co2_seq_t", "co2_emissions_t", "net_co2_balance_t")


@admin.register(EconomicBase)
class EconomicBaseAdmin(admin.ModelAdmin):
    list_display = ("city", "year", "capex", "opex", "gross_revenue", "pretax_net")
    list_filter = ("city",)
    ordering = ("city", "year")


@admin.register(Taxation)
class TaxationAdmin(admin.ModelAdmin):
    list_display = ("economic_base", "is_mad", "ir_mad", "total_tax", "posttax_net", "is_exonere")


@admin.register(FinancialPerformance)
class FinancialPerformanceAdmin(admin.ModelAdmin):
    list_display = ("city", "discount_rate", "npv_mad", "irr_pct", "bcr", "payback_years")
