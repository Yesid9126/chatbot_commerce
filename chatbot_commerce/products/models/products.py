"""Products model."""

# Django
from django.db import models
from django.contrib.postgres.fields import JSONField

# utilities
from chatbot_commerce.utils.models import ChetbootModel
from django.db.models.signals import post_save
from django.dispatch import receiver


class Product(ChetbootModel):
    """Main product model."""


    HOMBRE = 'HOMBRE'
    MUJER = 'MUJER'
    NIÑOS = 'NIÑOS'
    OTROS = 'OTROS'

    SUBCATEGORY_CHOICES = [
        (HOMBRE, HOMBRE),
        (MUJER, MUJER),
        (NIÑOS, NIÑOS),
        (OTROS, OTROS),
    ]
    id = models.AutoField(
        'Product id'
        primary_key=True,
    )

    name = models.CharField(
        'Product name',
        max_length=500
    )

    department_id = models.CharField(
        'Departament id',
        max_length=500
    )

    category_id = models.CharField(
        'Category id',
        max_length=500
    )

    brand_id = models.CharField(
        'Brand id',
        max_length=500
    )

    link_id = models.CharField(
        'link id',
        max_length=500
    )

    ref_id = models.CharField(
        'Reference id',
        max_length=500
    )

    is_visible = models.BooleanField(
        default=False,
    )

    description = models.TextField(
        'Description',
        max_length=500,
    )

    description_short = models.CharField(
        max_length=255
    )

    release_date = models.DateField()

    keywords = models.CharField(
        'Keywords',
        max_length=100
    )

    title = models.CharField(
        'Title',
        max_length=255
    )

    is_active = models.BooleanField(
        'Is active',
        default=255
    )

    tax_code = models.CharField(
        'Tax code',
        max_length=255
    )

    meta_tag_description = models.CharField(
        'Tag description',
        max_length=255
    )

    supplier_id = models.CharField(
        'Suplier id',
        max_length=255
    )

    show_without_stock = models.BooleanField(
        'Without stock',
        default=False
    )

    list_store_id = models.CharField(
        'List store',
        choices=SUBCATEGORY_CHOICES,
        default=SUBCATEGORY_CHOICES[0][3],
        max_length=255
    )

    adwords_remrketing_code = models.CharField(
        max_length=255,
        null=True
    )

    lomadee_campaing_code = models.CharField(
        max_length=255,
        null=True
    )


    def __str__(self):
        """Return product name|id."""
        return f'name:{self.name}'