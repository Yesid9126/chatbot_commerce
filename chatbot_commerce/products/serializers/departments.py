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


class CategoryModelSerializer(serializers.ModelSerializer):
    department = DepartmentModelSerializer(read_only=True)

    class Meta:
        model = Category
        fields = (
            'name',
            'department',
        )


class SubcategoryModelSerializer(serializers.ModelSerializer):
    category = CategoryModelSerializer(read_only=True)

    class Meta:
        model = Subcategory
        fields = (
            'name',
            'category',
        )


class SubcategoryTreeModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subcategory
        fields = (
            'name',
        )


class CategoryTreeModelSerializer(serializers.ModelSerializer):

    subcategories = SubcategoryTreeModelSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'pk',
            'name',
            'subcategories'
        )


class DepartmentTreeModelSerializer(serializers.ModelSerializer):

    categories = CategoryTreeModelSerializer(many=True)

    class Meta:
        model = Department
        fields = (
            'pk',
            'name',
            'categories'
        )
