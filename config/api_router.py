"""Api router general."""

from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

# Views
from chatbot_commerce.products.views import ProductViewset, DepartmentsViewset, BrandsViewset, AttributesViewset
from chatbot_commerce.orders.views import OrderViewSet


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(
    r'stores/(?P<store_slug_name>[-a-zA-Z0-9]+)/products',
    ProductViewset,
    basename='products'
)
router.register(
    r'stores/(?P<store_slug_name>[-a-zA-Z0-9]+)/departments',
    DepartmentsViewset,
    basename='departments'
)
router.register(
    r'orders',
    OrderViewSet,
    basename='orders'
)
router.register(
    r'stores/(?P<store_slug_name>[-a-zA-Z0-9]+)/brands',
    BrandsViewset,
    basename='brands'
)
router.register(
    r'stores/(?P<store_slug_name>[-a-zA-Z0-9]+)/attributes',
    AttributesViewset,
    basename='attributes'
)

app_name = "api"
urlpatterns = router.urls
