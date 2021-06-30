"""Stores models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.stores.models import StoresVtex

@admin.register(StoresVtex)
class StoresAdmin(admin.ModelAdmin):
    """Product model admin."""

    list_display = ['name', 'url']
    search_fields = ['name', 'url',]