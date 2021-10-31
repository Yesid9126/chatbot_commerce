"""Categories model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import BaseSlugnameAbstract, BaseExternalIdAbstract
from django.utils.translation import gettext as _


class Department(BaseSlugnameAbstract, BaseExternalIdAbstract):
    """Store departments."""

    stores = models.ManyToManyField(
        to='stores.Store', related_name='store_departments'
    )

    categories = models.ManyToManyField('stores.Category', verbose_name=_("Categories"))

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        default_related_name = 'departments'


class Category(BaseSlugnameAbstract, BaseExternalIdAbstract):
    """Departaments categories."""

    stores = models.ManyToManyField(
        to='stores.Store', related_name='store_categories'
    )

    subcategories = models.ManyToManyField('stores.Subcategory', verbose_name=_("Subcategories"))

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        default_related_name = 'categories'


class Subcategory(BaseSlugnameAbstract, BaseExternalIdAbstract):
    """Category subcategory."""

    stores = models.ManyToManyField(
        to='stores.Store', related_name='store_subcategories'
    )

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        default_related_name = 'subcategories'
