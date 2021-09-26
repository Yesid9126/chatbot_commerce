"""Product serializers."""

# Django rest framework
from chatbot_commerce.products.models.skus import AttributeType
from chatbot_commerce.products.models import Brand
from rest_framework import serializers

# Model
from chatbot_commerce.products.models import Product, FixedPrice, Price, Attribute, Skus


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


class FixedPriceModelSerializer(serializers.ModelSerializer):
    """FixedPrice model serializer"""

    date_ranges = serializers.SerializerMethodField(method_name='get_date_rages')

    class Meta:
        """Meta class"""
        model = FixedPrice
        fields = ['value', 'date_ranges']
        read_only_fields = fields

    def get_date_rages(self, obj):
        return obj.date_ranges.values('date_time_from', 'date_time_to')


class PriceModelSerializer(serializers.ModelSerializer):
    """Price model serializer"""

    fixed_prices = FixedPriceModelSerializer(many=True)

    class Meta:
        """Meta class"""
        model = Price
        fields = ['base_price', 'fixed_prices']
        read_only_fields = fields


class AttributeModelSerializer(serializers.ModelSerializer):
    """Attribute model serializer"""

    attribute_name = serializers.CharField(source='attribute_type')

    class Meta:
        """Meta class"""
        model = Attribute
        fields = (
            'attribute_name', 'value'
        )
        read_only_fields = fields


class SkuModelSerializer(serializers.ModelSerializer):
    """Sku model serializer"""

    price = PriceModelSerializer(many=True)
    images = serializers.SerializerMethodField(method_name='get_images')
    attributes = AttributeModelSerializer(many=True)
    sku_id = serializers.IntegerField(source='external_id')
    sku_name = serializers.CharField(source='name')
    seller_id = serializers.SerializerMethodField(method_name='get_seller_id')

    class Meta:
        """Meta class"""
        model = Skus
        fields = (
            'sku_id', 'seller_id', 'sku_name', 'total_quantity', 'images', 'price', 'attributes', 'is_active',
        )
        read_only_fields = fields

    def get_seller_id(self, obj):
        return list(obj.sku_seller.values_list('seller__seller_id', flat=True))[0]

    def get_images(self, obj):
        return obj.images.values_list('image_url', flat=True)


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    skus = SkuModelSerializer(many=True)
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
