from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProductConfig(AppConfig):
    """Product app config."""

    name = "chatbot_commerce.products"
    verbose_name = _("Product")
