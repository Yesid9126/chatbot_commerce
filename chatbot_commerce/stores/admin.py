"""Stores models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.stores.models import StoresVtex
from chatbot_commerce.products.models import StoreDepartment


class StoreDepartmensInline(admin.TabularInline):
    model = StoreDepartment
    extra = 0
    fields = ['department_name']


@admin.register(StoresVtex)
class StoresAdmin(admin.ModelAdmin):
    """Product model admin."""
    list_display = ['name', 'url_enviroment']
    search_fields = ['name', 'url_enviroment', ]
    inlines = [StoreDepartmensInline]
