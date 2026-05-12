from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"pigeons", views.PigeonViewSet, basename="pigeon")
router.register(r"couples", views.CoupleViewSet, basename="couple")
router.register(r"reproductions", views.ReproductionViewSet, basename="reproduction")
router.register(r"sorties", views.SortieViewSet, basename="sortie")
router.register(r"cages", views.CageViewSet, basename="cage")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", views.login_view, name="auth-login"),
    path("stats/", views.stats_view, name="stats"),
]
