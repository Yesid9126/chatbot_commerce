"""Products serializers."""

# Django rest framework
from chatbot_commerce.products.models.skus import Skus, Image
from rest_framework import serializers

# Model
from chatbot_commerce.products.models import ProductsApiVtex


class ImageSkuModelSerializer(serializers.ModelSerializer):
    """Image model serializer"""

    class Meta:
        """Meta class"""

        model = Image
        fields = (
            'image_url',
        )


class SkuModelSerializer(serializers.ModelSerializer):
    """Sku model serializer"""

    sku_images = ImageSkuModelSerializer(many=True)

    class Meta:
        """Meta class"""

        model = Skus
        fields = (
            'sku_id', 'product_id', 'sku_name', 'sku_images'
        )


class ProductsModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    products_sku = SkuModelSerializer(many=True)

    class Meta:
        """Meta class."""

        model = ProductsApiVtex
        fields = (
            'product_id', 'name', 'department_name', 'category_name', 'keywords', 'products_sku'
        )
        depth = 1
