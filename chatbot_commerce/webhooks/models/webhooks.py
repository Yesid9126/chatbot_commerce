"""Webhook models."""

# Django
from django.db import models
from django.contrib.postgres.fields import JSONField

# utilities
from chatbot_commerce.utils.models import ChatbootModel


class Order(ChatbootModel):
    """Order class."""

    DONE = 'DONE'
    PENDING = 'PENDING'
    FAILED = 'FAILED'

    STATUS_CHOICES = [
        (DONE, DONE),
        (FAILED, FAILED),
        (PENDING, PENDING),
    ]
    status = models.CharField(
        'Status',
        max_length=255,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    customer = models.CharField(
        max_length=100,
    )

    price = models.PositiveIntegerField(
        default=0,
    )

    hook_data = models.JSONField('Hook complete data', blank=True, null=True)

    def __str__(self):
        """Return order id."""
        return str(self.id)

    class Meta:
        """Meta class."""

        verbose_name = "Order"
        verbose_name_plural = "Orders"


class OrderItem(ChatbootModel):
    """Order item."""

    sku_unit = models.ForeignKey(
        to='products.Skus',
        on_delete=models.CASCADE,
        related_name='sku'
    )

    order = models.ForeignKey(
        to='Order',
        on_delete=models.CASCADE,
        related_name='item',
    )

    quantity = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    price = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    def __str__(self):
        """Return order id."""
        return str(self.sku_unit)

    class Meta:
        """Meta class."""

        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
