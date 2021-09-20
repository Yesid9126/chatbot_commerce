"""Product serializers."""

# Django rest framework
from chatbot_commerce.products.models.skus import AttributeType
from chatbot_commerce.products.models import Skus, Brand
from rest_framework import serializers

# Model
from chatbot_commerce.products.models import Product


class BrandsModelSerializer(serializers.ModelSerializer):
    """Brand model serializer"""

    class Meta:
        """Meta class."""

        model = Brand
        fields = [
            'external_id',
            'name',
            'title',
            'description'
        ]
        read_only_fields = fields


class SkuModelSerializer(serializers.ModelSerializer):
    """Sku model serializer"""

    price = serializers.SerializerMethodField('get_prices')
    images = serializers.SerializerMethodField('get_images')
    attributes = serializers.SerializerMethodField('get_attributes')

    class Meta:
        """Meta class"""
        model = Skus
        fields = (
            'sku_id', 'sku_name', 'total_quantity', 'images',
            'price',
            'attributes', 'is_active'
        )
        read_only_fields = fields

    def get_images(self, obj):
        return obj.get_images

    def get_prices(self, obj):
        return obj.get_prices

    def get_attributes(self, obj):
        return obj.get_attributes


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    skus = serializers.SerializerMethodField('get_skus')
    brand = serializers.SerializerMethodField('get_brand')
    tree_categories = serializers.SerializerMethodField('get_tree_categories')
    product_id = serializers.CharField(source='external_id')

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
        read_only_fields = fields

    def get_tree_categories(self, obj):
        if obj.sub_category:
            category_tree = {
                'name': obj.sub_category.name,
                'category': {
                    'name': obj.category.name,
                    'department': {
                        'name': obj.department.name
                    }
                }
            }
        elif obj.category:
            category_tree = {
                'name': obj.category.name,
                'department': {
                    'name': obj.department.name
                }
            }
        else:
            category_tree = {
                'name': obj.department.name
            }
        return category_tree

    def get_brand(self, obj):
        if obj.brand:
            brand = {
                'name': obj.brand.name,
                'slug_name': obj.brand.slug_name
            }
        return brand

    def get_skus(self, obj):
        return obj.skus.values_list('serializer_data', flat=True)


class AttributeTypeModelSerializer(serializers.ModelSerializer):
    """Attribute type model serializer."""

    attributes = serializers.SerializerMethodField('get_attributes')

    class Meta:
        """Meta class."""

        model = AttributeType
        fields = [
            'attributes'
        ]
        read_only_fields = fields

    def __init__(self, instance=None, data=None, **kwargs):
        self.attributes = kwargs['context']
        super().__init__(instance=instance, **kwargs)

    def get_attributes(self, obj):
        return self.attributes.filter(attribute_type=obj).values_list('value', flat=True).distinct()

    def to_representation(self, instance):
        self.fields[instance.name] = self.fields['attributes']
        return super().to_representation(instance)
