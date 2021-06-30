"""Categories model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import ChatbootModel

class SotreDepartment(ChatbootModel):
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
        null=True,
        blank=True
    )

    title = models.CharField(
        'Title',
        max_length=500,
    )
    
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

    def __str__(self):
        """Return category name."""
        return f'name:{self.category}'

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"