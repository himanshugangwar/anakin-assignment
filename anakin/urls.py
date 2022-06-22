"""
anakin URL Configuration
"""

from core.views import *
from django.contrib import admin
from django.urls import include, path
# import routers
from rest_framework import routers
from rest_framework.authtoken import views

# define the router
router = routers.DefaultRouter()

# define the router path and viewset to be used
router.register(r"brands", BrandViewSet)
router.register(r"product-details", ProductDetailViewSet)
router.register(r"retail-stores", RetailStoreViewSet)
router.register(r"retailers", RetailerViewSet)
router.register(r"products", ProductViewSet)
router.register(r"promotions", PromotionViewSet)
router.register(r"users", UserViewSet)
router.register(r"alert", AlertViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api/", include("rest_framework.urls")),
    path("api-token-auth/", views.obtain_auth_token),
]
