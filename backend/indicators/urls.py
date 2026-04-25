from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"cities", views.CityViewSet, basename="city")
router.register(r"communes", views.CommuneViewSet, basename="commune")
router.register(r"rooftops", views.RooftopViewSet, basename="rooftop")

urlpatterns = [
    path("", include(router.urls)),
    path("scenarios/", views.run_scenario, name="run-scenario"),
    path("cities/<str:city_code>/financial/", views.city_financial, name="city-financial"),
]
