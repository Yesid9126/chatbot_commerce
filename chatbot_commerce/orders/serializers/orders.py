"""Orders serializers."""

# Django rest framework
from rest_framework import serializers

# Models
from chatbot_commerce.orders.models import Order, OrderItem
from chatbot_commerce.products.models import Skus
from chatbot_commerce.stores.models import Store


class CreateOrderSerializer(serializers.Serializer):
    """Create order serializer."""

    customer = serializers.CharField(required=True)
    store = serializers.CharField(required=True)
    sku_ids = serializers.ListField(required=True)

    def create(self, data):
        """Order create."""
        sku_ids = data.get('sku_ids')
        customer = data.get('customer')
        store = Store.objects.filter(slug_name=data.get('store')).get()
        order = Order.objects.create(customer=customer, hook_data=data, store=store)
        for item in sku_ids:
            sku_id = item.get('sku_id')
            sku = Skus.objects.filter(external_id=sku_id).get()
            price = sku.price.get()
            price = price.base_price
            quantity = item.get('quantity')
            OrderItem.objects.create(
                order=order,
                sku_unit=sku,
                quantity=quantity,
                price=price
            )
        order = Order.objects.filter(id=order.id).get()
        quantities = order.item.values_list('quantity', flat=True)
        prices_items = order.item.values_list('price', flat=True)
        price_order = 0
        for price in range(0, len(prices_items)):
            price = prices_items[price] * int(quantities[price])
            price_order += price
        order = Order.objects.update_or_create(
            id=order.id,
            defaults={
                'price': price_order
            }
        )
        return order
