from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import CustomTokenObtainPairView
from django.urls import re_path
from django.views.static import serve
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from api import views
from drf_yasg import openapi
# from rest_framework.documentation import include_docs_urls
from django.conf import settings

# from django.conf.urls import url
schema_view = get_schema_view(
   openapi.Info(
      title="Voliere API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
router = DefaultRouter()
router.register(r"pigeons", views.PigeonViewSet, basename="pigeon")
router.register(r"couples", views.CoupleViewSet, basename="couple")
router.register(r"reproductions", views.ReproductionViewSet, basename="reproduction")
router.register(r"sorties", views.SortieViewSet, basename="sortie")
router.register(r"cages", views.CageViewSet, basename="cage")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", views.register, name="register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", views.me, name="me"),
   #  path('create-superadmin/', views.CreateSuperAdminView.as_view(), name='create-superadmin'),

    # Alias court (évite 404 si le client appelle /api/stats/)
    path("stats/", views.dashboard_stats, name="stats"),
    path("dashboard/stats/", views.dashboard_stats, name="dashboard_stats"),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
