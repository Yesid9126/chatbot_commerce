"""Stores models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.stores.models import Store, SaleChannel, Seller, SkuSeller, StoreAPIKey, TypeStore
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.admin import APIKeyModelAdmin


class InlineSkuAdmin(admin.TabularInline):
    extra = 0
    model = SaleChannel.skus.through


class InlineSellers(admin.TabularInline):
    extra = 0
    model = SaleChannel.sellers.through


@admin.register(Store)
class StoresAdmin(admin.ModelAdmin):
    """Product model admin."""
    list_display = ['name', 'slug_name', 'url_enviroment']
    exclude = ['slug_name']
    search_fields = ['name', 'url_enviroment']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    """Seller model admin."""
    list_display = ['name', 'seller_id']
    inlines = [InlineSellers]
    search_fields = list_display


@admin.register(SkuSeller)
class SkuSellerAdmin(admin.ModelAdmin):
    """Seller model admin."""
    list_display = ['seller_id', 'store', 'sku_id', 'is_active']
    list_filter = ['is_active', 'seller']
    search_fields = ['seller', 'store', 'sku', 'is_active']

    def seller_id(self, obj):
        return obj.seller.seller_id

    def sku_id(self, obj):
        return obj.sku.external_id

    def store(self, obj):
        return obj.seller.store


@admin.register(SaleChannel)
class SaleChannelAdmin(admin.ModelAdmin):
    """Sale channel model admin."""
    list_display = ['name', 'slug_name', 'is_active']
    exclude = ['slug_name', 'skus']
    search_fields = ['name']
    list_filter = ['is_active', 'store']
    inlines = [InlineSkuAdmin, InlineSellers]


admin.site.unregister(APIKey)
admin.site.register(TypeStore)


@admin.register(StoreAPIKey)
class StoreAPIKeyAdmin(APIKeyModelAdmin):
    """Store api key model admin."""

    list_display = ('is_active', 'verify', *APIKeyModelAdmin.list_display, 'email',)
    list_filter = ('is_active', 'verify', 'revoked',)
    list_display_links = ('prefix',)
    search_fields = ('name',)
