"""Api router general."""

from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

# Views
from chatbot_commerce.products.views import ProductViewset

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(
    r'stores/(?P<store_slug_name>[-a-zA-Z0-0_]+)/products',
    ProductViewset,
    basename='Product'
)

app_name = "api"
urlpatterns = router.urls
