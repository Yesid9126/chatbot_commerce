"""Products model."""

# Django
from django.db import models
from django.db.models import JSONField

# utilities
from chatbot_commerce.utils.models import ChatbootModel


    
class ProductsApiVtex(ChatbootModel):
    """Main product model."""

    product_id = models.CharField(
        'Vtex product Id',
        max_length=30,
    )

    name = models.CharField(
        'Product name',
        max_length=500,
        null=True,
        blank=True
    )

    link_id = models.CharField(
        'link id',
        max_length=500,
        null=True,
        blank=True
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
        null=True,
        blank=True
    )

    description_short = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    keywords = models.CharField(
        'Keywords',
        max_length=100,
        null=True,
        blank=True
    )

    title = models.CharField(
        'Title',
        max_length=500,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        'Is active',
        default=True
    )

    meta_tag_description = models.CharField(
        'Tag description',
        max_length=500,
        null=True,
        blank=True
    )

    show_without_stock = models.BooleanField(
        'Without stock',
        default=False
    )

    category = models.ForeignKey(
        to='products.CategoriesStore',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categories'
    )

    product_data = JSONField('Complete product data', null=True, blank=True)

    def __str__(self):
        """Return product name|id."""
        return f'name:{self.name}'
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    