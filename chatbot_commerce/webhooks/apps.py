from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WebhooksConfig(AppConfig):

    name = 'chatbot_commerce.webhooks'
    verbose_name = _("Webhooks")
