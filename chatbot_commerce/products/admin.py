"""Products models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.products.models import ProductsApiVtex, StoreDepartment, Skus, CategoriesStore


class StoreCategoriesInline(admin.TabularInline):
    model = CategoriesStore
    extra = 0
    fields = ['category_name']


class ProductsCategoriesInline(admin.TabularInline):
    model = ProductsApiVtex
    extra = 0
    fields = ['name']


class ProductsSkusInline(admin.TabularInline):
    model = Skus
    extra = 0
    fields = ['sku_id', 'product_id']


@admin.register(CategoriesStore)
class CategoriesAdmin(admin.ModelAdmin):
    """Departments model admin."""

    list_display = ['category_id', 'category_name']
    search_fields = ['category_id', 'category_name']
    inlines = [ProductsCategoriesInline]


@admin.register(StoreDepartment)
class DepartmentsAdmin(admin.ModelAdmin):
    """Departments model admin."""

    list_display = ['department_name', 'title']
    search_fields = ['department_name', 'title', 'categories']
    inlines = [StoreCategoriesInline]


@admin.register(ProductsApiVtex)
class ProductsAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_display = ['id', 'name', 'product_id']
    search_fields = ['name', 'product_id']
    inlines = [ProductsSkusInline]


@admin.register(Skus)
class SkusAdmin(admin.ModelAdmin):
    """Sku's model admin."""

    list_display = ['sku_id', 'sku_name', 'product_id']
    search_fields = ['sku_id', 'sku_name', 'product_id']
