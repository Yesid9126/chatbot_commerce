"""Departments serializers."""

# Django rest framework
from rest_framework import serializers

# Models
from chatbot_commerce.stores.models import (
    Department,
    Subcategory,
    Category
)


class DepartmentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = (
            'name',
        )
        read_only_fields = fields


class CategoryModelSerializer(serializers.ModelSerializer):
    department = DepartmentModelSerializer(read_only=True)

    class Meta:
        model = Category
        fields = (
            'name',
            'department',
        )
        read_only_fields = fields


class SubcategoryModelSerializer(serializers.ModelSerializer):
    category = CategoryModelSerializer(read_only=True)

    class Meta:
        model = Subcategory
        fields = (
            'name',
            'category',
        )
        read_only_fields = fields


class SubcategoryTreeModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subcategory
        fields = (
            'name',
        )
        read_only_fields = fields


class CategoryTreeModelSerializer(serializers.ModelSerializer):

    subcategories = serializers.SerializerMethodField(method_name='get_subcategories')

    class Meta:
        model = Category
        fields = (
            'pk',
            'name',
            'subcategories'
        )
        read_only_fields = fields

    def get_subcategories(self, obj):
        return obj.subcategories.values_list('name', flat=True)


class DepartmentTreeModelSerializer(serializers.ModelSerializer):

    categories = serializers.SerializerMethodField(method_name='get_categories')
    pk = serializers.IntegerField(source='external_id')

    class Meta:
        model = Department
        fields = (
            'pk',
            'name',
            'categories'
        )
        read_only_fields = fields

    def get_categories(self, obj):
        return [
            {
                'pk': category.external_id,
                'name': category.name,
                'subcategories': [
                    subcategory.name
                    for subcategory in category.q_subcategories
                ],
            }
            for category in obj.q_categories
        ]
