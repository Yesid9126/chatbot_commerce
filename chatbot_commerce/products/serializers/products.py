"""Product serializers."""

# Django rest framework
from chatbot_commerce.products.models.skus import FixedPrice, Price, Skus, Image, DateRange
from rest_framework import serializers

# Model
from chatbot_commerce.products.models import Product


class ImageSkuModelSerializer(serializers.ModelSerializer):
    """Image model serializer"""

    class Meta:
        """Meta class"""

        model = Image
        fields = (
            'image_url',
        )


class DateRangeModelSerializer(serializers.ModelSerializer):
    """Date range model serializer"""

    class Meta:
        """Meta class"""
        model = DateRange
        fields = (
            'date_time_from', 'date_time_to'
        )


class FixedPriceModelSerializer(serializers.ModelSerializer):
    """FixedPrice model serializer"""

    date_ranges = DateRangeModelSerializer(many=True)

    class Meta:
        """Meta class"""
        model = FixedPrice
        fields = ['trade_policy_id', 'value', 'min_quantity', 'date_ranges']


class PriceModelSerializer(serializers.ModelSerializer):
    """Price model serializer"""

    fixed_prices = FixedPriceModelSerializer(many=True)

    class Meta:
        """Meta class"""
        model = Price
        fields = ['base_price', 'fixed_prices']


class SkuModelSerializer(serializers.ModelSerializer):
    """Sku model serializer"""

    price = PriceModelSerializer(many=True)
    sku_images = ImageSkuModelSerializer(many=True)

    class Meta:
        """Meta class"""

        model = Skus
        fields = (
            'sku_id', 'product_id', 'sku_name', 'sku_images', 'price'
        )


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    Product_sku = SkuModelSerializer(many=True)

    class Meta:
        """Meta class."""

        model = Product
        fields = (
            'product_id', 'name', 'department_name', 'category_name', 'keywords', 'Product_sku'
        )
