"""Products serializers."""

# Django rest framework
from chatbot_commerce.products.models.skus import Skus
from django.db.models import fields
from rest_framework import serializers

# Model
from chatbot_commerce.products.models import ProductsApiVtex


class SkuModelSerializer(serializers.ModelSerializer):
    """Sku model serializer"""

    class Meta:
        """Meta class"""

        model = Skus
        fields = (
            'sku_id', 'product_id', 'specification'
        )
class ProductsModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    products_sku = SkuModelSerializer(many=True)
    class Meta:
        """Meta class."""

        model = ProductsApiVtex
        fields = (
            'product_id', 'name', 'keywords', 'products_sku'
        )
        depth = 1