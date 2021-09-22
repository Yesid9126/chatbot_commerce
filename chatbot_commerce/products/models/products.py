"""Product model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import AbstractCategory
from django.utils.translation import gettext as _


class Brand(AbstractCategory):
    store = models.ForeignKey(
        "stores.Store", verbose_name=_("Store"), on_delete=models.CASCADE,
        default=None, null=True
    )

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        default_related_name = 'brands'


class Product(AbstractCategory):
    """Main product model."""

    # Filter data
    is_visible = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        _('Is active'),
        default=True
    )
    show_without_stock = models.BooleanField(
        _('Without stock'),
        default=False
    )

    # Extra filter data
    keywords = models.TextField(_("Keywords"), blank=True, null=True)

    # Relationship filter
    store = models.ForeignKey(
        to='stores.Store',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    department = models.ForeignKey(
        to='products.Department',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    category = models.ForeignKey(
        to='products.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    sub_category = models.ForeignKey(
        to='products.Subcategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    # Extra data
    link_id = models.CharField(
        _('link id'),
        max_length=500,
        null=True,
        blank=True
    )
    reference_id = models.CharField(
        _('Reference id'),
        max_length=500,
        null=True,
        blank=True
    )
    description_short = models.TextField(_("Short description"), null=True, blank=True)
    meta_tag_description = models.TextField(_("Tag description"), null=True, blank=True)

    def __str__(self):
        """Return product name|id."""
        return f'{self.name}'

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Product"
        default_related_name = 'products'
