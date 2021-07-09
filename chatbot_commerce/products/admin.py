"""Products models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.products.models import ProductsApiVtex, StoreDepartment, Skus

@admin.register(ProductsApiVtex)
class ProductsAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_display = ['name', 'product_id']
    search_fields = ['name', 'product_id']


@admin.register(StoreDepartment)
class DepartmentsAdmin(admin.ModelAdmin):
    """Departments model admin."""

    list_display = ['department_name', 'title']
    search_fields = ['department_name', 'title', 'categories']


@admin.register(Skus)
class SkusAdmin(admin.ModelAdmin):
    """Sku's model admin."""

    list_display = ['sku_id', 'specification']

