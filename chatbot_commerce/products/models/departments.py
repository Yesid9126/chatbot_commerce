"""Categories model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import AbstractCategory


class Department(AbstractCategory):
    """Store departments."""

    store = models.ForeignKey(
        to='stores.Store',
        on_delete=models.CASCADE,
        related_name='departments',
    )

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class Category(AbstractCategory):
    """Departaments categories."""

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Subcategory(AbstractCategory):
    """Category subcategory."""

    category = models.ForeignKey(
        to='products.Category',
        on_delete=models.CASCADE,
        related_name='subcategories'
    )

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
