"""Products urls."""

# Django
from django.urls import include, path

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import products as products_views

router = DefaultRouter()
router.register(r'pilatos/products', products_views.ProductsViewset, basename='products')


urlpatterns = [
    path('', include(router.urls)),
]
