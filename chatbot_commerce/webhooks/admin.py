"""Webhooks models admin."""

# Django
from django.contrib import admin

# Models
from chatbot_commerce.webhooks.models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order model admin."""

    list_display = ['id', 'customer', 'status']
    search_fields = ['id', 'customer']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Order item admin."""

    list_display = ['order', 'quantity']
    search_fields = ['order__customer',]

