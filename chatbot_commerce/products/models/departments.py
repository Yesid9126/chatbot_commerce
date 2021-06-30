"""Categories model."""

# Django
from django.db import models
from django.db.models import JSONField

# utilities
from chatbot_commerce.utils.models import ChatbootModel

class StoreDepartment(ChatbootModel):
    """Store departmentss"""

    department = models.CharField(
        'Store department',
        max_length=50
    )

    url_department = models.CharField(
        'Url',
        max_length=5000,
        null=True,
        blank=True
    )

    categories = models.ForeignKey(
        'CategoriesStore', on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True
    )

    title = models.CharField(
        'Title',
        max_length=500,
    )

    department_json = JSONField('Complete department data', null=True, blank=True)
    
    def __str__(self):
        """Return Department name."""
        return f'name:{self.department}'

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

class CategoriesStore(ChatbootModel):
    """Departaments categories"""

    category = models.CharField(
        'Department category',
        max_length=50
    )

    products = models.ForeignKey(
        'products.ProductsApiVtex',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='products'
    )

    categories_json = JSONField('Complete categories data', null=True, blank=True)

    def __str__(self):
        """Return category name."""
        return f'name:{self.category}'

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"