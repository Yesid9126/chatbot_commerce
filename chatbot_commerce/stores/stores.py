"""Stores model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import ChatbootModel
# from chatbot_commerce.products.models.products import Product


class StoresVtex(ChatbootModel):
    """Stores model."""

    name = models.CharField(
        'Store Name',
        max_length=255,
    )

    url_enviroment = models.CharField(
        'Store Name',
        max_length=255,
    )

    api_key = models.CharField(
        'Appi key store',
        max_length=500
    )

    api_token = models.CharField(
        'Appi token store',
        max_length=500
    )

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='products'
    )

    @property
    def headers(self):
        headers = {
            "X-VTEX-API-AppKey": f"{self.api_key_value}",
            "X-VTEX-API-AppToken": f"{self.api_token_value}"
        }
        return headers
