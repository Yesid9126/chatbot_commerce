"""Categories model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import BaseSlugnameAbstract, BaseExternalIdAbstract, BaseAbstract


class Department(BaseSlugnameAbstract, BaseExternalIdAbstract):
    """Store departments."""

    stores = models.ManyToManyField(
        to='stores.Store', related_name='store_departments'
    )

    def __str__(self) -> str:
        if self.name:
            return self.name
        return super().__str__()

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        default_related_name = 'departments'


class Category(BaseAbstract):
    """Departaments categories."""

    store = models.ForeignKey(
        to='stores.Store', on_delete=models.CASCADE, related_name='store_categories'
    )

    department = models.ForeignKey(
        to='stores.Department', on_delete=models.SET_NULL, null=True
    )

    raw_json = None

    serializer_data = None

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        default_related_name = 'categories'


class Subcategory(BaseAbstract):
    """Category subcategory."""

    category = models.ForeignKey(
        to='stores.Category', on_delete=models.SET_NULL, null=True
    )

    raw_json = None

    serializer_data = None

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        default_related_name = 'subcategories'
