"""Orders models admin."""

# Django
from chatbot_commerce.products.models.skus import Skus
from django.contrib import admin

# Models
from chatbot_commerce.orders.models import Order, OrderItem


class InlineOrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['sku_unit', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order model admin."""

    list_display = ['id', 'customer', 'status', 'price']
    search_fields = ['id', 'customer']
    inlines = [InlineOrderItemAdmin]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Order item admin."""

    list_display = ['sku_id', 'order', 'sku_unit', 'price', 'id']
    search_fields = ['order__customer', ]

    def sku_id(self, obj):
        """Sku id."""
        return obj.sku_unit.sku_id
