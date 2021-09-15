"""Stores models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.stores.models import Store, SaleChannel


class InlineSkuAdmin(admin.TabularInline):
    extra = 0
    model = SaleChannel.skus.through


@admin.register(Store)
class StoresAdmin(admin.ModelAdmin):
    """Product model admin."""
    list_display = ['name', 'slug_name', 'url_enviroment']
    exclude = ['slug_name']
    search_fields = ['name', 'url_enviroment']


@admin.register(SaleChannel)
class SaleChannelAdmin(admin.ModelAdmin):
    """Sale channel model admin."""
    list_display = ['name', 'slug_name', 'is_active']
    exclude = ['slug_name', 'skus']
    search_fields = ['name']
    list_filter = ['is_active']
    inlines = [InlineSkuAdmin]
