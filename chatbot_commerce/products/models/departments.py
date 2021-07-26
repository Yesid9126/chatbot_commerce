"""Categories model."""

# Django
from django.db import models
from django.db.models import JSONField

# utilities
from chatbot_commerce.utils.models import ChatbootModel


class StoreDepartment(ChatbootModel):
    """Store departmentss"""

    department_id = models.CharField(
        'Department id',
        max_length=6,
        null=True,
        blank=True
    )

    department_name = models.CharField(
        'Department name',
        max_length=50
    )

    url_department = models.CharField(
        'Url department',
        max_length=5000,
        null=True,
        blank=True
    )

    has_children = models.BooleanField(
        default=False,
    )

    store = models.ForeignKey(
        to='stores.StoresVtex',
        on_delete=models.CASCADE,
        related_name='departments_store',
        null=True,
        blank=True
    )

    title = models.CharField(
        'Title',
        max_length=500,
    )

    tag_description = models.CharField(
        'Description',
        max_length=500,
        blank=True,
        null=True
    )

    department_json = JSONField('Complete department data', null=True, blank=True)

    def __str__(self):
        """Return Department name."""
        return f'name:{self.department_name}'

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class CategoriesStore(ChatbootModel):
    """Departaments categories"""

    category_id = models.CharField(
        max_length=6,
        null=True,
        blank=True
    )

    category_name = models.CharField(
        'Department category',
        max_length=50
    )

    has_children = models.BooleanField(
        default=False,
    )

    departments = models.ForeignKey(
        to='StoreDepartment',
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True
    )

    categories_json = JSONField('Complete categories data', null=True, blank=True)

    def __str__(self):
        """Return category name."""
        return self.category_name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
