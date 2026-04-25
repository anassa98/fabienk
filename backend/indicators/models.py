from decimal import Decimal

from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import JSONField


# ════════════════════════════════════════════════════════════════════════
# 1. GEOGRAPHY  (parents first)
# ════════════════════════════════════════════════════════════════════════


class City(models.Model):
    UNEMPLOYMENT_RATES_PCT = {
        "Casablanca": Decimal("19"),
        "Rabat":      Decimal("17"),
        "Marrakech":  Decimal("15"),
    }
    PER_CAPITA_FOOD_CONSUMPTION = Decimal("121.9")   # kg/person/year

    city_code = models.CharField(max_length=10, primary_key=True,
                                 help_text="e.g. 'CAS', 'RAB', 'MRK'")
    name      = models.CharField(max_length=50, unique=True)

    population            = models.PositiveIntegerField()
    unemployed_population = models.PositiveIntegerField(default=0)
    rooftop_area_m2       = models.BigIntegerField()
    ground_area_m2        = models.BigIntegerField(default=0)
    geometry              = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    annee_creation = models.IntegerField(help_text="Project start year")
    horizon_years  = models.IntegerField(default=20, help_text="Investment horizon N")

    food_demand                    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    employment_rate_total_pct      = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    employment_rate_unemployed_pct = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    buildings_per_farmer           = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    total_yield                = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    ssr_city                   = models.DecimalField(max_digits=8,  decimal_places=4, default=0)
    ssr_buildings_based        = models.DecimalField(max_digits=8,  decimal_places=4, default=0)
    yield_per_capita_city      = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    yield_per_capita_buildings = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    farmers = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name

    @property
    def unemployment_rate_pct(self):
        return self.UNEMPLOYMENT_RATES_PCT.get(self.name, Decimal("0"))

    @property
    def rooftops(self):
        return Rooftop.objects.filter(commune__city=self)

    @property
    def population_buildings(self):
        return sum((Decimal(r.population) for r in self.rooftops), Decimal("0"))

    def calculate_food_demand(self):
        self.food_demand = Decimal(self.population) * self.PER_CAPITA_FOOD_CONSUMPTION

    def calculate_total_yield(self):
        self.total_yield = sum(
            (r.productivity_indicators.total_yield for r in self.rooftops
             if hasattr(r, "productivity_indicators")),
            Decimal("0"),
        )

    def calculate_ssr_city(self):
        denom = Decimal(self.population) * self.PER_CAPITA_FOOD_CONSUMPTION
        self.ssr_city = (self.total_yield / denom) * 100 if denom else Decimal("0")

    def calculate_yield_per_capita_city(self):
        self.yield_per_capita_city = (self.total_yield / Decimal(self.population)
                                      if self.population else Decimal("0"))

    def calculate_ssr_buildings_based(self):
        denom = self.population_buildings * self.PER_CAPITA_FOOD_CONSUMPTION
        self.ssr_buildings_based = (self.total_yield / denom) * 100 if denom else Decimal("0")

    def calculate_yield_per_capita_buildings_based(self):
        pop = self.population_buildings
        self.yield_per_capita_buildings = self.total_yield / pop if pop else Decimal("0")

    def calculate_number_of_farmers(self):
        self.farmers = int(sum(
            (r.social_indicators.labor_person_total for r in self.rooftops
             if hasattr(r, "social_indicators")),
            Decimal("0"),
        ))

    def calculate_employment_rate_total_pct(self):
        if self.population:
            self.employment_rate_total_pct = (
                Decimal(self.farmers) / Decimal(self.population) * 100
            )

    def calculate_employment_rate_unemployed_pct(self):
        unemp = Decimal(self.population) * self.unemployment_rate_pct / Decimal("100")
        if unemp:
            self.employment_rate_unemployed_pct = (
                Decimal(self.farmers) / unemp * 100
            )

    def calculate_buildings_per_farmer(self):
        n_rooftops = self.rooftops.count()
        if self.farmers:
            self.buildings_per_farmer = Decimal(n_rooftops) / Decimal(self.farmers)

    def calculate_all(self):
        self.calculate_food_demand()
        self.calculate_total_yield()
        self.calculate_number_of_farmers()
        self.calculate_ssr_city()
        self.calculate_yield_per_capita_city()
        self.calculate_ssr_buildings_based()
        self.calculate_yield_per_capita_buildings_based()
        self.calculate_employment_rate_total_pct()
        self.calculate_employment_rate_unemployed_pct()
        self.calculate_buildings_per_farmer()


class Commune(models.Model):
    commune_code = models.CharField(max_length=20, primary_key=True)
    name         = models.CharField(max_length=80)
    city         = models.ForeignKey(City, on_delete=models.CASCADE, related_name="communes")
    geometry     = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)

    def __str__(self):
        return self.name


class Rooftop(models.Model):
    TECHNIQUE_CHOICES = [("soilbased", "Soil-based"), ("soilless", "Soilless")]
    SYSTEM_CHOICES    = [("monoculture", "Monoculture"), ("multiculture", "Multiculture")]

    id         = models.AutoField(primary_key=True)
    commune    = models.ForeignKey(Commune, on_delete=models.PROTECT, related_name="rooftops")
    area       = models.DecimalField(max_digits=14, decimal_places=2)
    perimeter  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    population = models.PositiveIntegerField(default=0)
    ratio_a_p  = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    technique  = models.CharField(max_length=20, choices=TECHNIQUE_CHOICES)
    system     = models.CharField(max_length=20, choices=SYSTEM_CHOICES)
    geometry   = gis_models.PolygonField(srid=4326, null=True, blank=True)

    @property
    def city(self):
        return self.commune.city

    def __str__(self):
        return f"Rooftop {self.id}"


# ════════════════════════════════════════════════════════════════════════
# 2. INDICATORS PER ROOFTOP  (each 1:1 with Rooftop)
# ════════════════════════════════════════════════════════════════════════


class ProductivityIndicators(models.Model):
    YIELD_PER_SURFACE = {
        "soilbased": Decimal("4"),
        "soilless":  Decimal("28"),
    }
    PER_CAPITA_FOOD_DEMAND = Decimal("121.9")

    rooftop          = models.OneToOneField(Rooftop, on_delete=models.CASCADE,
                                            related_name="productivity_indicators")
    total_yield      = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    yield_per_capita = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    food_demand      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    ssr              = models.DecimalField(max_digits=8,  decimal_places=4, default=0)

    @property
    def technique(self):
        return self.rooftop.technique

    @property
    def system(self):
        return self.rooftop.system

    def calculate_yield(self, tier_k=2):
        yps = self.YIELD_PER_SURFACE[self.technique]
        if self.system == "monoculture":
            self.total_yield = self.rooftop.area * yps
        else:
            self.total_yield = self.rooftop.area * yps * Decimal(tier_k)

    def calculate_yield_per_capita(self):
        if self.rooftop.population:
            self.yield_per_capita = self.total_yield / Decimal(self.rooftop.population)

    def calculate_food_demand(self):
        self.food_demand = Decimal(self.rooftop.population) * self.PER_CAPITA_FOOD_DEMAND

    def calculate_ssr(self):
        if self.food_demand:
            self.ssr = (self.total_yield / self.food_demand) * 100

    def calculate_all(self, tier_k=2):
        self.calculate_yield(tier_k)
        self.calculate_food_demand()
        self.calculate_yield_per_capita()
        self.calculate_ssr()


class SocialIndicators(models.Model):
    LABOR_PERSON_M2 = {
        "soilbased": Decimal("0.001"),
        "soilless":  Decimal("0.005"),
    }
    JOB_CREATION_COST_MAD = Decimal("27060.36")

    rooftop                     = models.OneToOneField(Rooftop, on_delete=models.CASCADE,
                                                       related_name="social_indicators")
    labor_person_m2             = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    labor_person_total          = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    total_labor_cost            = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    accessibility_m2_per_person = models.DecimalField(max_digits=14, decimal_places=4, default=0)

    def init_labor_person_m2(self):
        self.labor_person_m2 = self.LABOR_PERSON_M2[self.rooftop.technique]

    def calculate_labor_person_total(self):
        self.labor_person_total = self.labor_person_m2 * self.rooftop.area

    def calculate_total_labor_cost(self):
        self.total_labor_cost = self.labor_person_total * self.JOB_CREATION_COST_MAD

    def calculate_accessibility(self):
        if self.labor_person_total:
            self.accessibility_m2_per_person = self.rooftop.area / self.labor_person_total

    def calculate_all(self):
        self.init_labor_person_m2()
        self.calculate_labor_person_total()
        self.calculate_total_labor_cost()
        self.calculate_accessibility()


class EnvironmentalIndicators(models.Model):
    DMC_PCT             = Decimal("15.0")
    HARVEST_INDEX_PCT   = Decimal("50.0")
    CARBON_FRACTION_AVG = Decimal("0.4100")
    CO2_C_RATIO         = Decimal("44") / Decimal("12")
    EF_SOILBASED_HIGH   = Decimal("0.07")
    EF_SOILLESS         = Decimal("0.57")

    env_id  = models.AutoField(primary_key=True)
    rooftop = models.OneToOneField(Rooftop, on_delete=models.CASCADE,
                                   related_name="environmental_indicators")

    crop_dry_matter_kg   = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_dry_biomass_kg = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    carbon_content_kg    = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    co2_seq_kg           = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    co2_seq_t            = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    organ_carbon_shares  = JSONField(default=dict, blank=True)

    co2_emissions_kg    = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    co2_emissions_t     = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    emission_components = JSONField(default=dict, blank=True)

    net_co2_balance_kg = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    net_co2_balance_t  = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    @property
    def emission_factor(self):
        return self.EF_SOILLESS if self.rooftop.technique == "soilless" else self.EF_SOILBASED_HIGH

    def compute(self):
        D = Decimal
        fresh = self.rooftop.productivity_indicators.total_yield

        self.crop_dry_matter_kg   = fresh * (self.DMC_PCT / D("100"))
        self.total_dry_biomass_kg = self.crop_dry_matter_kg / (self.HARVEST_INDEX_PCT / D("100"))
        self.carbon_content_kg    = self.total_dry_biomass_kg * self.CARBON_FRACTION_AVG
        self.co2_seq_kg           = self.carbon_content_kg * self.CO2_C_RATIO
        self.co2_seq_t            = self.co2_seq_kg / D("1000")

        self.co2_emissions_kg = fresh * self.emission_factor
        self.co2_emissions_t  = self.co2_emissions_kg / D("1000")

        self.net_co2_balance_kg = self.co2_seq_kg - self.co2_emissions_kg
        self.net_co2_balance_t  = self.net_co2_balance_kg / D("1000")


# ════════════════════════════════════════════════════════════════════════
# 3. ECONOMICS, TAXATION, FINANCIAL PERFORMANCE  (per City, per year)
# ════════════════════════════════════════════════════════════════════════


class EconomicBase(models.Model):
    SEUIL_AGRI        = Decimal("5000000")
    MAINTENANCE_CAPEX = Decimal("0")

    city          = models.ForeignKey(City, on_delete=models.CASCADE, related_name="economic_bases")
    year          = models.IntegerField()
    capex         = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    opex          = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    gross_revenue = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    pretax_net    = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        unique_together = [("city", "year")]
        ordering = ["city", "year"]

    @property
    def age(self):
        return self.year - self.city.annee_creation

    @property
    def total_yield(self):
        return sum(
            (r.productivity_indicators.total_yield for r in self.city.rooftops
             if hasattr(r, "productivity_indicators")),
            Decimal("0"),
        )

    @property
    def technique(self):
        first = self.city.rooftops.first()
        return first.technique if first else None

    @property
    def historique_ca(self):
        return list(
            EconomicBase.objects
            .filter(city=self.city, year__lt=self.year)
            .order_by("year")
            .values_list("year", "gross_revenue")
        )

    def calculate_gross_revenue(self, price_per_kg):
        self.gross_revenue = self.total_yield * Decimal(str(price_per_kg))

    def calculate_pretax_net(self):
        deduction = self.opex
        if self.technique == "soilless" and self.age > 0 and self.age % 4 == 0:
            deduction += self.MAINTENANCE_CAPEX
        self.pretax_net = max(self.gross_revenue - deduction, Decimal("0"))


class Taxation(models.Model):
    SEUIL_AGRI    = Decimal("5000000")
    ANNUAL_SALARY = Decimal("36000")
    IR_BRACKETS = [
        (Decimal("40000"),  Decimal("0.00"), Decimal("0")),
        (Decimal("60000"),  Decimal("0.10"), Decimal("4000")),
        (Decimal("80000"),  Decimal("0.20"), Decimal("10000")),
        (Decimal("100000"), Decimal("0.30"), Decimal("18000")),
        (Decimal("180000"), Decimal("0.34"), Decimal("22000")),
        (None,              Decimal("0.37"), Decimal("27400")),
    ]

    economic_base  = models.OneToOneField(EconomicBase, on_delete=models.CASCADE, related_name="taxation")
    is_mad         = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    ir_mad         = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    tva_perdue_mad = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    cotisation_min = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    css_mad        = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    tp_mad         = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    tsc_mad        = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_tax      = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    posttax_net    = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_exonere     = models.BooleanField(default=False)

    def _agri_exempt(self):
        eb = self.economic_base
        if eb.gross_revenue >= self.SEUIL_AGRI:
            return False
        history = [c for _, c in eb.historique_ca]
        if not any(c >= self.SEUIL_AGRI for c in history):
            return True
        last_breach = max((i for i, c in enumerate(history) if c >= self.SEUIL_AGRI), default=-1)
        cons = 0
        for c in history[last_breach + 1:]:
            cons = cons + 1 if c < self.SEUIL_AGRI else 0
        return cons >= 3

    def _is_rate(self, bnf):
        if bnf <= 300_000:        return Decimal("0.175")
        elif bnf <= 1_000_000:    return Decimal("0.20")
        elif bnf <= 100_000_000:  return Decimal("0.2275")
        else:                     return Decimal("0.34")

    def _ir_per_worker(self):
        for ceiling, rate, deduction in self.IR_BRACKETS:
            if ceiling is None or self.ANNUAL_SALARY <= ceiling:
                return max(self.ANNUAL_SALARY * rate - deduction, Decimal("0"))
        return Decimal("0")

    def _total_labors(self):
        return sum(
            (r.social_indicators.labor_person_total for r in self.economic_base.city.rooftops
             if hasattr(r, "social_indicators")),
            Decimal("0"),
        )

    def calculate_is(self):
        self.is_exonere = self._agri_exempt()
        if self.is_exonere:
            self.is_mad = Decimal("0")
            return
        bnf = self.economic_base.pretax_net
        self.is_mad = bnf * self._is_rate(bnf)

    def calculate_cotisation_min(self):
        if self.is_exonere or self.economic_base.age * 12 < 36:
            self.cotisation_min = Decimal("0")
            return
        self.cotisation_min = max(
            self.economic_base.gross_revenue * Decimal("0.0025"),
            Decimal("3000"),
        )

    def calculate_ir(self):
        self.ir_mad = self._ir_per_worker() * self._total_labors()

    def calculate_css(self):
        bnf = self.economic_base.pretax_net
        if self.is_exonere or bnf < 1_000_000:
            self.css_mad = Decimal("0")
            return
        if bnf <= 5_000_000:    rate = Decimal("0.015")
        elif bnf <= 10_000_000: rate = Decimal("0.025")
        elif bnf <= 40_000_000: rate = Decimal("0.035")
        else:                   rate = Decimal("0.05")
        self.css_mad = bnf * rate

    def calculate_tp(self, vla):
        if self.economic_base.age < 5:
            self.tp_mad = Decimal("0")
            return
        self.tp_mad = max(Decimal(str(vla)) * Decimal("0.10"), Decimal("300"))

    def calculate_tsc(self, vla, zone="urbaine"):
        rate = Decimal("0.105") if zone == "urbaine" else Decimal("0.065")
        self.tsc_mad = Decimal(str(vla)) * rate

    def calculate_tva_perdue(self, achats_non_exoneres_ht):
        self.tva_perdue_mad = Decimal(str(achats_non_exoneres_ht)) * Decimal("0.20")

    def calculate_total_tax(self):
        is_du = max(self.is_mad, self.cotisation_min)
        self.total_tax = is_du + self.ir_mad + self.css_mad + self.tp_mad + self.tsc_mad

    def calculate_posttax_net(self):
        self.posttax_net = self.economic_base.pretax_net - self.total_tax

    def calculate_all(self, vla, zone="urbaine", achats_non_exoneres_ht=Decimal("0")):
        self.calculate_is()
        self.calculate_cotisation_min()
        self.calculate_css()
        self.calculate_ir()
        self.calculate_tp(vla)
        self.calculate_tsc(vla, zone)
        self.calculate_tva_perdue(achats_non_exoneres_ht)
        self.calculate_total_tax()
        self.calculate_posttax_net()


class FinancialPerformance(models.Model):
    city          = models.OneToOneField(City, on_delete=models.CASCADE, related_name="financial_performance")
    discount_rate = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal("0.08"))

    npv_mad                  = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    irr_pct                  = models.DecimalField(max_digits=8,  decimal_places=4, null=True, blank=True)
    ror_pct                  = models.DecimalField(max_digits=8,  decimal_places=4, default=0)
    discounted_ror_pct       = models.DecimalField(max_digits=8,  decimal_places=4, default=0)
    bcr                      = models.DecimalField(max_digits=8,  decimal_places=4, default=0)
    payback_years            = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)
    payback_discounted_years = models.DecimalField(max_digits=6,  decimal_places=2, null=True, blank=True)

    def _cash_flows(self):
        N = self.city.horizon_years
        bases = list(
            self.city.economic_bases
                .select_related("taxation")
                .filter(year__gte=self.city.annee_creation,
                        year__lte=self.city.annee_creation + N)
                .order_by("year")
        )
        flows = []
        for eb in bases:
            posttax = eb.taxation.posttax_net if hasattr(eb, "taxation") else eb.pretax_net
            cf = posttax
            if eb.age == 0:
                cf -= eb.capex
            elif eb.technique == "soilless" and eb.age > 0 and eb.age % 4 == 0:
                cf -= eb.MAINTENANCE_CAPEX
            flows.append(cf)
        return flows

    def calculate_npv(self):
        flows = self._cash_flows()
        r = self.discount_rate
        self.npv_mad = sum((cf / (1 + r) ** t for t, cf in enumerate(flows)), Decimal("0"))

    def calculate_irr(self):
        flows = self._cash_flows()
        try:
            import numpy_financial as npf
            result = npf.irr([float(cf) for cf in flows])
            self.irr_pct = Decimal(str(result)) * 100 if result is not None else None
        except Exception:
            self.irr_pct = None

    def calculate_ror(self):
        flows = self._cash_flows()
        investment = -flows[0] if flows and flows[0] < 0 else Decimal("0")
        total_profit = sum(flows[1:], Decimal("0"))
        self.ror_pct = (total_profit / investment) * 100 if investment else Decimal("0")

    def calculate_discounted_ror(self):
        flows = self._cash_flows()
        r = self.discount_rate
        investment = -flows[0] if flows and flows[0] < 0 else Decimal("0")
        discounted_profit = sum(
            (cf / (1 + r) ** t for t, cf in enumerate(flows[1:], start=1)),
            Decimal("0"),
        )
        self.discounted_ror_pct = (discounted_profit / investment) * 100 if investment else Decimal("0")

    def calculate_bcr(self):
        flows = self._cash_flows()
        r = self.discount_rate
        benefits = sum((cf / (1 + r) ** t for t, cf in enumerate(flows) if cf > 0), Decimal("0"))
        costs    = sum((-cf / (1 + r) ** t for t, cf in enumerate(flows) if cf < 0), Decimal("0"))
        self.bcr = benefits / costs if costs else Decimal("0")

    def calculate_payback(self):
        flows = self._cash_flows()
        cum = Decimal("0")
        for t, cf in enumerate(flows):
            cum += cf
            if cum >= 0:
                self.payback_years = t
                return
        self.payback_years = None

    def calculate_payback_discounted(self):
        flows = self._cash_flows()
        r = self.discount_rate
        cum = Decimal("0")
        for t, cf in enumerate(flows):
            cum += cf / (1 + r) ** t
            if cum >= 0:
                self.payback_discounted_years = t
                return
        self.payback_discounted_years = None

    def calculate_all(self):
        self.calculate_npv()
        self.calculate_irr()
        self.calculate_ror()
        self.calculate_discounted_ror()
        self.calculate_bcr()
        self.calculate_payback()
        self.calculate_payback_discounted()
