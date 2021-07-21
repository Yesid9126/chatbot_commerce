"""Products serializers."""

# Django rest framework
from django.db.models import fields
from rest_framework import serializers

# Model
from chatbot_commerce.products.models import ProductsApiVtex


class ProductsModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    class Meta:
        """Meta class."""

        model = ProductsApiVtex
        fields = (
            'product_id', 'name', 'link_id', 'products_sku'
        )