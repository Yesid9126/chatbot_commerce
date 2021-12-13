"""Product models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.stores.models import (
    Department,
    Category,
    Subcategory,
    Brand,
    Product,
    Image,
    Price,
    DateRange,
    Sku,
    FixedPrice,
    Attribute,
    AttributeType
)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Subcategory model admin."""

    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('name', 'category', 'external_id',)


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    readonly_fields = ('name', 'store', 'department', 'external_id',)


@admin.register(Department)
class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug_name']
    search_fields = ['name', 'slug_name']
    readonly_fields = ('stores', 'external_id',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug_name']
    search_fields = ['name', 'slug_name']
    readonly_fields = ('stores', 'external_id',)


class InlineSku(admin.TabularInline):
    model = Sku
    extra = 0
    fields = ('external_id', 'name', 'total_quantity',)
    readonly_fields = fields


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_select_related = ('store', 'department', 'category', 'sub_category', 'brand',)
    list_display = ('external_id', 'name', 'is_active', 'store', 'brand', 'department', 'category', 'sub_category',)
    list_display_links = ('external_id', 'name',)
    search_fields = ('name', 'external_id', 'department', 'brand', 'category', 'sub_category',)
    list_filter = ('store__store_type', 'is_active', 'store',)
    exclude_fields = ('search_vector', 'search', 'link_id', 'reference_id', 'show_without_stock',)
    readonly_fields = ('external_id', 'name', 'is_active', 'store', 'brand', 'department', 'category', 'sub_category', 'raw_json', 'serializer_data', 'search_vector',)
    inlines = [InlineSku]


@admin.register(Image)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('image_url',)
    readonly_fields = ('image_url', 'skus', 'products', 'store',)


class InlineImageAdmin(admin.TabularInline):
    model = Image
    extra = 0
    fields = ('image_id', 'name', 'image_url',)
    readonly_fields = fields


class InlinePriceAdmin(admin.TabularInline):
    model = Price
    extra = 0
    fields = ['base_price', 'price']
    readonly_fields = ('price',)


@admin.register(Sku)
class SkuAdmin(admin.ModelAdmin):
    """Sku's model admin."""

    readonly_fields = ('raw_json', 'product', 'search_vector',)
    list_display = ['external_id', 'name', 'total_quantity']
    search_fields = ['external_id', 'name']
    list_filter = ['is_active', 'is_inventoried', 'reference_stock_id']


@admin.register(DateRange)
class DateRangeAdmin(admin.ModelAdmin):
    """Sku's model admin."""
    list_display = ('date_time_from', 'date_time_to',)


class InlineDateRangeAdmin(admin.TabularInline):
    model = DateRange
    extra = 0
    fields = ['date_time_from', 'date_time_to']


@admin.register(FixedPrice)
class FixedPriceAdmin(admin.ModelAdmin):
    """Price model admin."""
    readonly_fields = ('price',)
    list_display = ['price', 'trade_policy_id', 'value']
    # inlines = [InlineDateRangeAdmin]


class InlineFixedPriceAdmin(admin.TabularInline):
    model = FixedPrice
    extra = 0
    fields = ['value', 'trade_policy_id']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    """Price model admin."""
    readonly_fields = ('sku',)
    list_display = ['sku_id', 'sku', 'base_price']
    inlines = [InlineFixedPriceAdmin]

    def sku_id(self, obj):
        """Sku id."""
        return obj.sku.external_id


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    """Price model admin."""

    readonly_fields = ('skus', 'attribute_type',)
    list_display = ['sku_id', 'attribute_type', 'value']
    search_fields = ['value']

    def sku_id(self, obj):
        """Sku id."""
        return obj.skus.values_list('external_id', flat=True)


# admin.site.register(Attribute)
admin.site.register(AttributeType)
