"""Products model."""

# Django
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError

# utilities
from chatbot_commerce.utils.models import ChatbootModel
from chatbot_commerce.products.models.stores import StoresVtex
from django.db.models.signals import post_save
from django.dispatch import receiver

class Colors(models.Model):
    """Colors model."""
    colors = models.CharField('Colores',max_length=15)

    def clean(self):
        colors = self.colors.capitalize()
        self.colors = colors
        try:
            if Colors.objects.get(colors=colors):
                raise ValidationError('Este color ya fue registrado')
        except Colors.DoesNotExist:
            return super().clean()

    class Meta:
        """Meta class."""
        verbose_name = 'Colores'
        verbose_name_plural = 'Colores'

    def __str__(self):
        return self.colors

class Sizes(models.Model):
    """Size model."""
    sizes = models.CharField('Sizes',max_length=4) 

    class Meta:
        """Size meta class."""
        verbose_name = 'Sizes'
        verbose_name_plural = 'Sizes'
        ordering = ['sizes']

    def clean(self):
        """Validation for not repeat sizes in admin"""
        sizes = self.sizes.upper()
        self.sizes = sizes
        try:
            if Sizes.objects.get(sizes=sizes):
                raise ValidationError('Esta talla ya fue registrada')
        except Sizes.DoesNotExist:
            return super().clean()

    def __str__(self):
        return self.sizes 
    
class CategoryProduts(models.Model):
    """Category products."""

    name = models.CharField(
        max_length=255
    )
class Product(ChatbootModel):
    """Main product model."""

    product_id = models.SlugField(
        'Vtex product Id',
        unique=True,
        max_length=255
    )

    name = models.CharField(
        'Product name',
        max_length=500
    )

    sku = models.CharField(
        'Product sku',
        unique=True,
        max_length=500
    )

    category = models.ForeignKey(
        CategoryProduts,
        on_delete=models.CASCADE,
    )

    link_id = models.CharField(
        'link id',
        max_length=500
    )

    reference_id = models.CharField(
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

    show_without_stock = models.BooleanField(
        'Without stock',
        default=False
    )


    def __str__(self):
        """Return product name|id."""
        return f'name:{self.name}'

class ProductVariants(models.Model):
    """Model product variant."""

    colors = models.ForeignKey(
        Colors,
        on_delete=models.CASCADE,
        verbose_name='Colors'
    )

    sizes = models.ForeignKey(
        Sizes,
        on_delete=models.CASCADE,
        verbose_name='Sizes'
    )
    