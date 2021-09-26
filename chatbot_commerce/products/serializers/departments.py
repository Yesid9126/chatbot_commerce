"""Departments serializers."""

# Django rest framework
from rest_framework import serializers

# Models
from chatbot_commerce.products.models import (
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

    subcategories = SubcategoryTreeModelSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'pk',
            'name',
            'subcategories'
        )
        read_only_fields = fields


class DepartmentTreeModelSerializer(serializers.ModelSerializer):

    categories = CategoryTreeModelSerializer(many=True)

    class Meta:
        model = Department
        fields = (
            'pk',
            'name',
            'categories'
        )
        read_only_fields = fields
