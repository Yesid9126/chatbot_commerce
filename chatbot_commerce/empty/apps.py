from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EmptyConfig(AppConfig):
    """Stores app config."""

    name = "chatbot_commerce.empty"
    verbose_name = _("Empty")
