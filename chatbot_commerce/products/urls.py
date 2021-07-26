"""Products urls."""

# Django
from django.urls import include, path
from chatbot_commerce.utils.departments_categories import get_departments

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# Views
from .views import products as products_views

router = DefaultRouter()
router.register(r'pilatos/products', products_views.ProductsViewset, basename='products')


urlpatterns = [
    path('', include(router.urls)),
    path("vtex/pilatos", get_departments, name='tienda_detail_api_view')
]
