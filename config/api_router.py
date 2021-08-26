"""Api router general."""

from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

# Views
from chatbot_commerce.products.views import ProductViewset, DepartmentsViewset
from chatbot_commerce.webhooks.views import WebHookViewSet

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
    r'hooks/orders',
    WebHookViewSet,
    basename='orders'
)

app_name = "api"
urlpatterns = router.urls
