"""Products models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.products.models import *

@admin.register(ProductsApiVtex)
class ProductsAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_display = ['name', 'product_id', 'sku']
    search_fields = ['name', 'product_id', 'sku' ]


@admin.register(SotreDepartment)
class DepartmentsAdmin(admin.ModelAdmin):
    """Departments model admin."""

    list_display = ['department', 'title']
    search_fields = ['department', 'title', 'categories']


@admin.register(Skus)
class SkusAdmin(admin.ModelAdmin):
    """Sku's model admin."""

    list_display = ['sku_id', 'specification']

