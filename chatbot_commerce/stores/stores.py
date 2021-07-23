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

    url = models.URLField()

    app_key = models.CharField(
        max_length=500
    )

    token = models.CharField(
        max_length=500
    )

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='products'
    )
