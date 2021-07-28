"""Products urls."""

# Django
from django.urls import include, path
from chatbot_commerce.utils.products import get_products_vtex_store

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import products as products_views

router = DefaultRouter()
router.register(r'pilatos/products', products_views.ProductsViewset, basename='products')


urlpatterns = [
    path('', include(router.urls)),
    path("vtex/pilatos", get_products_vtex_store, name='tienda_detail_api_view')
]
