"""Skus model."""

# Django
from django.db import models
from django.db.models import JSONField

# utilities
from chatbot_commerce.utils.models import ChatbootModel
from chatbot_commerce.stores.models import StoresVtex


class Skus(ChatbootModel):
    """Store departmentss"""

    sku_id = models.CharField(
        'Sku ID',
        max_length=10
    )

    product_id = models.CharField(
        'Product ID',
        max_length=10,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=False,
    )

    specification = models.CharField(
        'Specification sku',
        max_length=255,
    )

    refID = models.CharField(
        max_length=100,
        blank=True
    )

    is_kit = models.BooleanField(
        default=False
    )

    comercial_condition_id = models.CharField(
        max_length=100,
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


class Price(ChatbootModel):
    store = models.ForeignKey(StoresVtex, on_delete=models.CASCADE)
    sku = models.ForeignKey(Skus, on_delete=models.CASCADE, related_name='price')
    listPrice = models.BigIntegerField('List price', null=True, blank=True)
    costPrice = models.BigIntegerField('Cost price', null=True, blank=True)
    markup = models.BigIntegerField('Mark up', null=True, blank=True)
    basePrice = models.BigIntegerField('Base price', null=True, blank=True)

    class Meta:
        verbose_name = 'Price'
        verbose_name_plural = "Price's"


class FixedPrices(ChatbootModel):
    store = models.ForeignKey(StoresVtex, on_delete=models.CASCADE)
    price = models.ForeignKey(Price, on_delete=models.CASCADE, related_name='fixedPrices')
    tradePolicyId = models.CharField('Trade porlice ID', max_length=50)
    value = models.BigIntegerField('Value', null=True, blank=True)
    listPrice = models.BigIntegerField('List price', null=True, blank=True)
    minQuantity = models.IntegerField('Minimun quantity', null=True, blank=True)

    class Meta:
        verbose_name = "FixedPrice"
        verbose_name_plural = "Fixed price's"
