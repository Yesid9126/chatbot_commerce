"""Product models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.products.models import (
    Department,
    Category,
    Subcategory,
    Brand,
    Product,
    Image,
    Price,
    DateRange,
    Skus,
    FixedPrice
)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Subcategory model admin."""

    list_display = ['name', 'slug_name', 'category']
    search_fields = ['name', 'slug_name']


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug_name', 'department']
    search_fields = ['name', 'slug_name']
    list_filter = ['department']


@admin.register(Department)
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug_name']
    search_fields = ['name', 'slug_name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug_name']
    search_fields = ['name', 'slug_name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_display = ['name', 'store', 'sub_category', 'department', 'category', 'brand']
    search_fields = ['name', 'external_id']


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
