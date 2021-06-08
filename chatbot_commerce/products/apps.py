from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProductsConfig(AppConfig):
    """Products app config."""

    name = "chatbot_commerce.products"
    verbose_name = _("Products")
