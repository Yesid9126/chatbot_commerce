"""Product model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import AbstractCategory


class Brand(AbstractCategory):
    pass


class Product(AbstractCategory):
    """Main product model."""
    store = models.ForeignKey(
        to='stores.Store',
        on_delete=models.CASCADE,
        related_name='products',
        null=True, blank=True
    )

    sub_category = models.ForeignKey(
        to='products.Subcategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    department = models.ForeignKey(
        to='products.Department',
        on_delete=models.CASCADE,
        related_name='products',
        null=True, blank=True
    )

    category = models.ForeignKey(
        to='products.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='products'
    )

    link_id = models.CharField(
        'link id',
        max_length=500,
        null=True,
        blank=True
    )

    reference_id = models.CharField(
        'Reference id',
        max_length=500,
        null=True,
        blank=True
    )

    is_visible = models.BooleanField(
        default=False,
    )

    description_short = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    keywords = models.CharField(
        'Keywords',
        max_length=100,
        null=True,
        blank=True
    )

    title = models.CharField(
        'Title',
        max_length=500,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        'Is active',
        default=True
    )

    meta_tag_description = models.CharField(
        'Tag description',
        max_length=500,
        null=True,
        blank=True
    )

    show_without_stock = models.BooleanField(
        'Without stock',
        default=False
    )

    def __str__(self):
        """Return product name|id."""
        return f'name:{self.name}'

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Product"
