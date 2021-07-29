"""Categories model."""

# Django
from django.db import models
from django.db.models import JSONField, fields

# utilities
from chatbot_commerce.utils.models import ChatbootModel


class Department(ChatbootModel):
    """Store departmentss"""

    department_id = models.CharField(
        'Department id',
        max_length=6,
        null=True,
        blank=True
    )

    department_name = models.CharField(
        'Department name',
        max_length=50,
        null=True,
        blank=True
    )

    url_department = models.CharField(
        'Url department',
        max_length=5000,
        null=True,
        blank=True
    )

    has_children = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )


    title = models.CharField(
        'Title',
        max_length=500,
        null=True,
        blank=True
    )

    tag_description = models.CharField(
        'Description',
        max_length=500,
        blank=True,
        null=True
    )

    subcategories = models.ManyToManyField(
        'products.Category',
        through='products.Subcategory',
        through_fields = ('department', 'category')
    )



    department_json = JSONField('Complete department data', null=True, blank=True)

    def __str__(self):
        """Return Department name."""
        return f'name:{self.department_name}'

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class Subcategory(models.Model):
    """Category subcategory."""

    subcategory_name = models.CharField(
        'Subcategory name',
        max_length=255,
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        to=Department,
        on_delete=models.CASCADE,
        related_name='childs'
    )

    category = models.ForeignKey(
        to='products.Category',
        on_delete=models.CASCADE,
        related_name='childs'
    )

    category_tree = models.JSONField(
        'Children for categories',
        null=True,
        blank=True
    )
    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"


class Category(ChatbootModel):
    """Departaments categories"""

    category_id = models.CharField(
        max_length=6,
        null=True,
        blank=True
    )

    category_name = models.CharField(
        'Department category',
        max_length=50,
        null=True,
        blank=True
    )

    has_children = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )

    departments = models.ForeignKey(
        to='Department',
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
