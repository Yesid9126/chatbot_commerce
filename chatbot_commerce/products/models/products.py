"""Product model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import AbstractCategory
from django.utils.translation import gettext as _


class Brand(AbstractCategory):
    store = models.ForeignKey(
        "stores.Store", verbose_name=_("Store"), on_delete=models.CASCADE,
        default=None, null=True
    )

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        default_related_name = 'brands'


class Product(AbstractCategory):
    """Main product model."""

    # Filter data
    is_visible = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        _('Is active'),
        default=True
    )
    show_without_stock = models.BooleanField(
        _('Without stock'),
        default=False
    )

    # Extra filter data
    keywords = models.TextField(_("Keywords"), blank=True, null=True)

    # Relationship filter
    store = models.ForeignKey(
        to='stores.Store',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    department = models.ForeignKey(
        to='products.Department',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    category = models.ForeignKey(
        to='products.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    sub_category = models.ForeignKey(
        to='products.Subcategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    # Extra data
    link_id = models.CharField(
        _('link id'),
        max_length=500,
        null=True,
        blank=True
    )
    reference_id = models.CharField(
        _('Reference id'),
        max_length=500,
        null=True,
        blank=True
    )
    description_short = models.TextField(_("Short description"), null=True, blank=True)
    meta_tag_description = models.TextField(_("Tag description"), null=True, blank=True)

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_product
        return super().save(*args, **kwargs)

    def __str__(self):
        """Return product name|id."""
        return f'name:{self.name}'

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Product"
        default_related_name = 'products'

    @property
    def get_product(self):
        product_dict = {
            'id': self.external_id,
            'name': self.name,
            'keywords': self.keywords,
            'brand': self.get_brand,
            'tree_categories': self.category_tree
        }
        return product_dict

    @property
    def get_brand(self):
        brand_dict = {
            'name': self.brand.name,
            'slug_name': self.brand.slug_name
        }
        return brand_dict

    @property
    def category_tree(self):
        if self.sub_category:
            category_tree_dict = {
                'name': self.sub_category.name,
                'category': {
                    'name': self.category.name,
                    'department': {
                        'name': self.department.name
                    }
                }
            }
        elif self.category:
            category_tree_dict = {
                'name': self.category.name,
                'department': {
                    'name': self.department.name
                }
            }
        elif self.department:
            category_tree_dict = {
                'name': self.department.name
            }
        else:
            category_tree_dict = {}
        return category_tree_dict
