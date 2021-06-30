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

    categories = models.ForeignKey(
        'CategoriesStore', on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    title = models.CharField(
        'Title',
        max_length=500,
    )

class CategoriesStore(ChatbootModel):
    """Departaments categories"""

    category = models.CharField(
        'Department category',
        max_length=50
    )