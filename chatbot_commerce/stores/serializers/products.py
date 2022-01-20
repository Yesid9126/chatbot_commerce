"""Product serializers."""

# Django rest framework
from chatbot_commerce.stores.models.skus import AttributeType
from rest_framework import serializers

# Model
from chatbot_commerce.stores.models import Product


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    skus = serializers.SerializerMethodField(method_name='get_skus')
    brand = serializers.SerializerMethodField('get_brand')
    tree_categories = serializers.SerializerMethodField('get_tree_categories')
    product_id = serializers.IntegerField(source='external_id')
    images = serializers.SerializerMethodField(method_name='get_images')

    class Meta:
        """Meta class."""

        model = Product
        fields = [
            'product_id',
            'name',
            'keywords',
            'brand',
            'tree_categories',
            'images',
            'skus',
        ]
        read_only_fields = fields

    def get_images(self, obj):
        return [image.image_url for image in obj.q_images]

    def get_skus(self, obj):
        return [
            {
                'sku_id': sku.external_id,
                'seller_id': sku.sellers_id[0] if sku.sellers_id else None,
                'sku_name': sku.name,
                'total_quantity': sku.total_quantity,
                'images': sku.images_url,
                'price': sku.price_data,
                'attributes': sku.attributes_data,
                'is_active': sku.is_active
            }
            for sku in obj.q_skus
        ]

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

        super().__init__(instance=instance, **kwargs)
        self.attributes = kwargs['context']

    def get_attributes(self, obj):
        return self.attributes.filter(attribute_type=obj).values_list('value', flat=True).distinct()

    def to_representation(self, instance):
        self.fields[instance.name] = self.fields['attributes']
        return super().to_representation(instance)
