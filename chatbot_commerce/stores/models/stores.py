"""Stores model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import ChatbootModel
# from chatbot_commerce.products.models.products import Product

class StoresVtex(ChatbootModel):
    """Stores model."""

    name = models.CharField(
        max_length=255,
    )

    url_enviroment = models.URLField(
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
        return f'sku:{self.sku_id}'

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"
