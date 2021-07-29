"""Stores model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import ChatbootModel


class StoresVtex(ChatbootModel):
    """Stores model."""

    name = models.CharField(
        max_length=255,
    )

    url_enviroment = models.CharField(
        max_length=500
    )

    appi_key = models.CharField(
        max_length=500
    )

    api_token = models.CharField(
        max_length=500
    )

    def __str__(self):
        """Return store name."""
        return f'Store:{self.name}'

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"

    @property
    def headers(self):
        headers = {
            "X-VTEX-API-AppKey": f"{self.appi_key}",
            "X-VTEX-API-AppToken": f"{self.api_token}"
        }
        return headers
