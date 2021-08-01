"""Products models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.products.models import (
    ProductsApiVtex, Department,
    Skus,
    Category,
    Subcategory,
    Image,
    Price,
    FixedPrice,
    DateRange
)


class ProductsSkusInline(admin.TabularInline):
    model = Skus
    extra = 0
    fields = ['sku_name', 'sku_id', 'product_id']


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


class CategoriessInline(admin.TabularInline):
    model = Category
    extra = 0
    fields = ['category_name', 'category_id']


@admin.register(Department)
class DepartmentsAdmin(admin.ModelAdmin):
    """Departments model admin."""

    list_display = ['department_name', 'title']
    search_fields = ['department_name', 'title', 'categories']
    inlines = [CategoriessInline]


@admin.register(ProductsApiVtex)
class ProductsAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_display = ['id', 'name', 'product_id']
    search_fields = ['name', 'product_id']
    inlines = [ProductsSkusInline]


@admin.register(Image)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['sku', 'image_url']


class InlineImageAdmin(admin.TabularInline):
    model = Image
    estra = 0
    fields = ['archive_id', 'name', 'image_url']


class InlinePriceAdmin(admin.TabularInline):
    model = Price
    estra = 0
    fields = ['base_price', 'price']


@admin.register(Skus)
class SkusAdmin(admin.ModelAdmin):
    """Sku's model admin."""

    list_display = ['sku_id', 'sku_name', 'product_id']
    search_fields = ['sku_id', 'sku_name', 'product_id']
    inlines = [InlineImageAdmin, InlinePriceAdmin]


@admin.register(DateRange)
class DateRangeAdmin(admin.ModelAdmin):
    """Sku's model admin."""

    list_display = ['fixed_price', 'date_time_from', 'date_time_to']


class InlineDateRangeAdmin(admin.TabularInline):
    model = DateRange
    extra = 0
    fields = ['date_time_from', 'date_time_to']


@admin.register(FixedPrice)
class FixedPriceAdmin(admin.ModelAdmin):
    """Price model admin."""

    list_display = ['price', 'trade_policy_id', 'value']
    inlines = [InlineDateRangeAdmin]


class InlineFixedPriceAdmin(admin.TabularInline):
    model = FixedPrice
    extra = 0
    fields = ['value', 'trade_policy_id']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    """Price model admin."""

    list_display = ['sku', 'base_price']
    inlines = [InlineFixedPriceAdmin]
