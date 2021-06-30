"""Skus model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import ChatbootModel

class Skus(ChatbootModel):
    """Store departmentss"""

    sku_id = models.CharField(
        'Sku',
        max_length=50
    )

    specification = models.CharField(
        'Specification sku',
        max_length=50
    )

    refID = models.PositiveIntegerField()

    is_kit = models.BooleanField(
        default=False
    )

    comercial_condition_id = models.PositiveIntegerField()

    def __str__(self):
        """Return product name|id."""
        return f'sku:{self.sku_id}'

    class Meta:
        verbose_name = "Sku"
        verbose_name_plural = "Sku's"