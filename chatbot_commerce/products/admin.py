"""Products models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.products.models import *

@admin.register(ProductsApiVtex)
class ProductsAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_display = ['name','product_id', 'sku']


