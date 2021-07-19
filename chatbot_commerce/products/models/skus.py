"""Skus model."""

# Django
from django.db import models
from django.db.models import JSONField

# utilities
from chatbot_commerce.utils.models import ChatbootModel

class Skus(ChatbootModel):
    """Store departmentss"""

    sku_id = models.CharField(
        'Sku ID',
        max_length=50
    )

    product_id = models.CharField(
        'Product ID',
        max_length=50,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=False,
    )

    specification = models.CharField(
        'Specification sku',
        max_length=50,
    )

    refID = models.PositiveIntegerField(
        default=0,
        blank=True
    )

    is_kit = models.BooleanField(
        default=False
    )

    comercial_condition_id = models.PositiveIntegerField(
        default=0,
        blank=True
    )

    products = models.ForeignKey(
        to='products.ProductsApiVtex',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='products_sku'
    )

    sku_json = JSONField(
        'Complete sku data',
        null=True,
        blank=True
    )

    def __str__(self):
        """Return sku id."""
        return f'sku:{self.specification}'

    class Meta:
        verbose_name = "Sku"
        verbose_name_plural = "Sku's"