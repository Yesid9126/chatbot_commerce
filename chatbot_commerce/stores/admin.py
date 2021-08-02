"""Stores models admin."""

# Django
from django.contrib import admin
# Models
from chatbot_commerce.stores.models import StoresVtex
from chatbot_commerce.products.models import Department


class DepartmentInline(admin.TabularInline):
    """Department inline"""
    model = Department
    extra = 0
    fields = ['department_name', 'department_id']


@admin.register(StoresVtex)
class StoresAdmin(admin.ModelAdmin):
    """Product model admin."""
    list_display = ['name', 'url_enviroment']
    search_fields = ['name', 'url_enviroment', ]
    inlines = [DepartmentInline]
