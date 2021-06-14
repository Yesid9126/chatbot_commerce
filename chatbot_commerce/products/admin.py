# Django
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# Models
from chatbot_commerce.products.models import Product,StoresVtex


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    pass


@admin.register(StoresVtex)
class StoresAdmin(admin.ModelAdmin):
    pass


