"""Products urls."""

# Django
from django.urls import include, path

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import products as products_view

router = DefaultRouter()
router.register(r'products', products_view.ProductsViewSet, basename='products')


urlpatterns = [
    path('', include(router.urls)),
]