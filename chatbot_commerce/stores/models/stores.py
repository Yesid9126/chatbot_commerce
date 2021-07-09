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

    url_enviroment = models.CharField(
        max_length=500
    )

    appi_key = models.CharField(
        max_length=500
    )

    api_token = models.CharField(
        max_length=500
    )

    departments = models.ForeignKey(
        to='products.StoreDepartment',
        on_delete=models.CASCADE,
        related_name='departments_store',
        null=True,
        blank=True
    )

    categories = models.ForeignKey(
        to='products.CategoriesStore',
        on_delete=models.CASCADE,
        related_name='categories_store',
        null=True,
        blank=True
    )

    def __str__(self):
        """Return store name."""
        return f'sku:{self.sku_id}'

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

