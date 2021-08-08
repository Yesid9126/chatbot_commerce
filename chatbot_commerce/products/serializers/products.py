"""Product serializers."""

# Django rest framework
from chatbot_commerce.products.models.skus import Attribute
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


class AttributeModelSerializer(serializers.ModelSerializer):
    """Attribute model serializer"""

    attribute_name = serializers.CharField(source='attribute_type')

    class Meta:
        """Meta class"""
        model = Attribute
        fields = (
            'attribute_name', 'value'
        )


class SkuModelSerializer(serializers.ModelSerializer):
    """Sku model serializer"""

    price = PriceModelSerializer(many=True)
    sku_images = ImageSkuModelSerializer(many=True)
    attributes = AttributeModelSerializer(many=True)

    class Meta:
        """Meta class"""
        model = Skus
        fields = (
            'sku_id', 'sku_name', 'sku_images', 'price', 'attributes', 'is_active'
        )


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    skus = serializers.SerializerMethodField('get_skus')
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

    def get_skus(self, obj):
        skus = Skus.objects.filter(product=obj, is_active=True)
        return SkuModelSerializer(skus, many=True).data
