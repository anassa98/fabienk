from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

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


class ProductivityIndicatorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductivityIndicators
        exclude = ["id", "rooftop"]


class SocialIndicatorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialIndicators
        exclude = ["id", "rooftop"]


class EnvironmentalIndicatorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalIndicators
        exclude = ["env_id", "rooftop"]


class RooftopListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""
    productivity = ProductivityIndicatorsSerializer(
        source="productivity_indicators", read_only=True
    )
    social = SocialIndicatorsSerializer(source="social_indicators", read_only=True)
    environmental = EnvironmentalIndicatorsSerializer(
        source="environmental_indicators", read_only=True
    )
    commune_name = serializers.CharField(source="commune.name", read_only=True)
    city_code = serializers.CharField(source="commune.city.city_code", read_only=True)

    class Meta:
        model = Rooftop
        fields = [
            "id", "commune", "commune_name", "city_code",
            "area", "perimeter", "population", "ratio_a_p",
            "technique", "system",
            "productivity", "social", "environmental",
        ]


class RooftopGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON FeatureCollection output for the map."""
    productivity = ProductivityIndicatorsSerializer(
        source="productivity_indicators", read_only=True
    )
    social = SocialIndicatorsSerializer(source="social_indicators", read_only=True)
    environmental = EnvironmentalIndicatorsSerializer(
        source="environmental_indicators", read_only=True
    )
    commune_name = serializers.CharField(source="commune.name", read_only=True)

    class Meta:
        model = Rooftop
        geo_field = "geometry"
        fields = [
            "id", "commune", "commune_name",
            "area", "perimeter", "population",
            "technique", "system",
            "productivity", "social", "environmental",
        ]


class CommuneSerializer(serializers.ModelSerializer):
    rooftop_count = serializers.SerializerMethodField()

    class Meta:
        model = Commune
        fields = ["commune_code", "name", "city", "rooftop_count"]

    def get_rooftop_count(self, obj):
        return obj.rooftops.count()


class CitySerializer(serializers.ModelSerializer):
    rooftop_count = serializers.SerializerMethodField()
    commune_count = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = "__all__"

    def get_rooftop_count(self, obj):
        return obj.rooftops.count()

    def get_commune_count(self, obj):
        return obj.communes.count()


class TaxationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxation
        exclude = ["id"]


class EconomicBaseSerializer(serializers.ModelSerializer):
    taxation = TaxationSerializer(read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = EconomicBase
        fields = "__all__"


class FinancialPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialPerformance
        fields = "__all__"


class ScenarioRequestSerializer(serializers.Serializer):
    """Body of POST /api/scenarios/."""
    city_code = serializers.CharField()
    horizon_years = serializers.IntegerField(required=False, min_value=1, max_value=50)
    discount_rate = serializers.DecimalField(
        max_digits=8, decimal_places=4, required=False
    )
    price_per_kg = serializers.DecimalField(max_digits=10, decimal_places=2, default=10)
    capex_per_m2 = serializers.DecimalField(max_digits=10, decimal_places=2, default=500)
    opex_per_m2 = serializers.DecimalField(max_digits=10, decimal_places=2, default=20)
    vla = serializers.DecimalField(max_digits=18, decimal_places=2, default=0)
    zone = serializers.ChoiceField(choices=["urbaine", "periurbaine"], default="urbaine")
    achats_non_exoneres_ht = serializers.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    tier_k = serializers.IntegerField(default=2, min_value=1)


class ScenarioResultSerializer(serializers.Serializer):
    city = CitySerializer()
    financial = FinancialPerformanceSerializer()
    cash_flows = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=2))
    economic_bases = EconomicBaseSerializer(many=True)
