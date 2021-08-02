"""Categories model."""

# Django
from django.db import models
from django.db.models import JSONField
from slugify import slugify

# utilities
from chatbot_commerce.utils.models import ChatbootModel


class Department(ChatbootModel):
    """Store departments."""

    department = models.ForeignKey(
        to='stores.Store',
        on_delete=models.CASCADE,
        related_name='childs'
    )

    name = models.CharField(max_length=255)
    slug_name = models.SlugField(max_length=255, null=True, blank=True)
    extenal_id = models.IntegerField()
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)

    subcategories = models.ManyToManyField(
        'products.Category',
        through='products.Subcategory',
        through_fields=('department', 'category')
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

    name = models.CharField(max_length=255)
    slug_name = models.SlugField(max_length=255, null=True, blank=True)
    extenal_id = models.IntegerField()
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    category_tree = models.JSONField(
        'Children for categories',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)


class Category(ChatbootModel):
    """Departaments categories."""

    name = models.CharField(max_length=255)
    slug_name = models.SlugField(max_length=255, null=True, blank=True)
    extenal_id = models.IntegerField()
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)

    category_json = JSONField('Complete categories data', null=True, blank=True)

    def __str__(self):
        """Return category name."""
        return self.category_name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
