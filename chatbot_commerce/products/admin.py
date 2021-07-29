"""Products models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.products.models import ProductsApiVtex, Department, Skus, Category, Subcategory, Image, Price, FixedPrices


# class CategoriesInline(admin.TabularInline):
#     model = Categories
#     extra = 0
#     fields = ['category_name']


# class ProductsCategoriesInline(admin.TabularInline):
#     model = ProductsApiVtex
#     extra = 0
#     fields = ['name']


# class ProductsSkusInline(admin.TabularInline):
#     model = Skus
#     extra = 0
#     fields = ['sku_id', 'product_id']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Departments model admin."""

    list_display = ['subcategory_name', 'department', 'category']
    search_fields = ['subcategory_name', 'department', 'category']


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    """Departments model admin."""

    list_display = ['category_id', 'category_name']
    search_fields = ['category_id', 'category_name']
    # inlines = [ProductsCategoriesInline]


@admin.register(Department)
class DepartmentsAdmin(admin.ModelAdmin):
    """Departments model admin."""

    list_display = ['department_name', 'title']
    search_fields = ['department_name', 'title', 'categories']
    # inlines = [CategoriesInline]


@admin.register(ProductsApiVtex)
class ProductsAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_display = ['id', 'name', 'product_id']
    search_fields = ['name', 'product_id']
    # inlines = [ProductsSkusInline]


@admin.register(Skus)
class SkusAdmin(admin.ModelAdmin):
    """Sku's model admin."""

    list_display = ['sku_id', 'sku_name', 'product_id']
    search_fields = ['sku_id', 'sku_name', 'product_id']


@admin.register(Image)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image_url']


class InlineFixedPrice(admin.TabularInline):
    model = FixedPrices
    extra = 0
    fields = ['store', 'value', 'tradePolicyId']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    """Price model admin."""

    list_display = ['store', 'sku']
    inlines = [InlineFixedPrice]


@admin.register(FixedPrices)
class FixedPriceAdmin(admin.ModelAdmin):
    """Price model admin."""

    list_display = ['store', 'price', 'tradePolicyId']
