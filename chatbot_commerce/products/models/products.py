"""Products model."""

# Django
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError

# utilities
from chatbot_commerce.utils.models import ChatbootModel
from django.db.models.signals import post_save
from django.dispatch import receiver

    
class ProductsApiVtex(ChatbootModel):
    """Main product model."""

    product_id = models.SlugField(
        'Vtex product Id',
        unique=True,
        max_length=255
    )

    name = models.CharField(
        'Product name',
        max_length=500
    )

    sku = models.CharField(
        'Product sku',
        unique=True,
        max_length=500
    )


    link_id = models.CharField(
        'link id',
        max_length=500
    )

    reference_id = models.CharField(
        'Reference id',
        max_length=500
    )

    is_visible = models.BooleanField(
        default=False,
    )

    description = models.TextField(
        'Description',
        max_length=500,
    )

    description_short = models.CharField(
        max_length=255
    )

    release_date = models.DateField()

    keywords = models.CharField(
        'Keywords',
        max_length=100
    )

    title = models.CharField(
        'Title',
        max_length=255
    )

    is_active = models.BooleanField(
        'Is active',
        default=255
    )

    tax_code = models.CharField(
        'Tax code',
        max_length=255
    )

    meta_tag_description = models.CharField(
        'Tag description',
        max_length=255
    )

    show_without_stock = models.BooleanField(
        'Without stock',
        default=False
    )


    def __str__(self):
        """Return product name|id."""
        return f'name:{self.name}'

    