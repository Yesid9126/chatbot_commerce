"""Product serializers."""

# Django rest framework
from chatbot_commerce.products.models import FixedPrice, Price, Skus, Image, DateRange, Brand
from rest_framework import serializers

# Model
from chatbot_commerce.products.models import Product

# Serializer
from chatbot_commerce.products.serializers.departments import (
    CategoryModelSerializer,
    SubcategoryModelSerializer,
    DepartmentModelSerializer
)


class ImageSkuModelSerializer(serializers.ModelSerializer):
    """Image model serializer"""

    class Meta:
        """Meta class"""

        model = Image
        fields = (
            'image_url',
        )


class BrandModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = (
            'name',
            'slug_name',
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
        fields = ['value', 'date_ranges']


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
            'sku_id', 'sku_name', 'sku_images', 'price'
        )


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    skus = SkuModelSerializer(many=True)
    brand = BrandModelSerializer(read_only=True)
    tree_categories = serializers.SerializerMethodField('get_tree_categories')
    product_id = serializers.CharField(source='pk')

    class Meta:
        """Meta class."""

        model = Product
        fields = [
            'product_id',
            'name',
            'keywords',
            'brand',
            'tree_categories',
            'skus',
        ]

    def get_tree_categories(self, obj):
        if obj.sub_category:
            return SubcategoryModelSerializer(obj.sub_category).data
        elif obj.category:
            return CategoryModelSerializer(obj.category).data
        return DepartmentModelSerializer(obj.department).data
