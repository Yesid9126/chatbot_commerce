"""Skus model."""

from slugify import slugify

# Django
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

# utilities
from chatbot_commerce.utils.models import ChatbootModel, BaseAbstract, BaseRawAbstract
from django.utils.translation import gettext as _


class Skus(BaseAbstract):
    """Store departmentss"""

    # Filter data
    is_active = models.BooleanField(
        'Active sku',
        default=False,
        null=True,
        blank=True
    )
    is_inventoried = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )
    total_quantity = models.CharField(
        'Quantity sku',
        max_length=255,
        null=True,
        blank=True
    )
    search_attributes = models.TextField(_("Attributes search"), blank=True, null=True)
    search = models.TextField(_("Search"), blank=True, null=True)
    is_transported = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )
    is_kit = models.BooleanField(
        'sku is kit',
        default=False,
        null=True,
        blank=True
    )

    # Relationship filter
    product = models.ForeignKey(
        to='products.Product',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    sales_channels = models.ManyToManyField("stores.SaleChannel", verbose_name=_("Sales channel's"))

    # Extra data
    comercial_condition_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    manufacter_code = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    ref_id = models.CharField(
        'Reference id',
        max_length=100,
        null=True,
        blank=True
    )
    packaged_height = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    packaged_length = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    packaged_width = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    packaged_weight = models.CharField(
        'Packaged weight Kg',
        max_length=50,
        null=True,
        blank=True
    )
    reference_stock_id = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )

    def __str__(self):
        """Return sku id."""
        return f'{self.name}'
    
    def save(self, *args, **kwargs):

        array_sku_seller = list(self.sku_seller.values_list('seller__seller_id', flat=True))
        if array_sku_seller:
            seller = array_sku_seller[0]
        else:
            seller = None

        price = self.price.first()
        if price:
            price = price.serializer_data
        else:
            price=None

        self.serializer_data = {
            'sku_id': self.external_id,
            'seller_id': seller,
            'sku_name': self.name,
            'total_quantity': self.total_quantity,
            'images': list(self.images.values_list('image_url', flat=True)),
            'price': price,
            'attributes': list(self.attributes.values('value', attribute_name=models.F('attribute_type__name'))),
            'is_active': self.is_active
        }
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Sku"
        verbose_name_plural = "Sku's"
        default_related_name = 'skus'


class Image(ChatbootModel):
    """Image model"""

    # Filter data
    name = models.CharField(_("Name"), max_length=500, null=True, blank=True)
    image_id = models.CharField(_("Image external id"), max_length=50, null=True, blank=True)

    # Relationship filter
    sku = models.ForeignKey("products.Skus", on_delete=models.CASCADE)

    # Url data
    image_url = models.URLField(_("Image url"), max_length=2000, null=True, blank=True)

    class Meta:
        """Meta class"""

        verbose_name = 'Image'
        verbose_name_plural = "Image's"
        default_related_name = 'images'


class Price(BaseRawAbstract):
    """Price model"""

    list_price = models.BigIntegerField(_('List price'), null=True, blank=True)
    cost_price = models.BigIntegerField(_('Cost price'), null=True, blank=True)
    markup = models.BigIntegerField(_('Mark up'), null=True, blank=True)

    # Filter data
    base_price = models.BigIntegerField(_('Base price'), null=True, blank=True)

    # Relationship filter
    sku = models.ForeignKey(Skus, on_delete=models.CASCADE)

    class Meta:
        """Meta class"""

        verbose_name = 'Price'
        verbose_name_plural = "Price's"
        ordering = ['sku', 'cost_price']
        default_related_name = 'price'

    def save(self, *args, **kwargs):
        self.serializer_data = {
            'base_price': self.base_price,
            'fixed_prices': list(self.fixed_prices.values_list('serializer_data', flat=True))
        }
        return super().save(*args, **kwargs)

    def __str__(self):
        """Return sku price."""
        return f'sku:{self.base_price}'

@receiver(post_save, sender=Price)
def _post_save_price(sender, instance, *args, **kwargs):
    instance.sku.save()
    


class FixedPrice(BaseRawAbstract):
    """Fixed price model"""

    # Filter data
    trade_policy_id = models.CharField(_('Trade porlice ID'), max_length=50)
    value = models.BigIntegerField(_('Value'), null=True, blank=True)
    list_price = models.BigIntegerField(_('List price'), null=True, blank=True)
    min_quantity = models.IntegerField(_('Minimun quantity'), null=True, blank=True)

    # Relationship filter
    price = models.ForeignKey(Price, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.serializer_data = {
            'value': self.value,
            'date_ranges': list(self.date_ranges.values('date_time_from', 'date_time_to'))
        }
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Fixed price"
        verbose_name_plural = "Fixed price's"
        ordering = ['price', 'trade_policy_id']
        default_related_name = 'fixed_prices'


class DateRange(BaseRawAbstract):
    """Date range model"""

    # Filter data
    date_time_from = models.DateTimeField(_("From date time"), auto_now=False, auto_now_add=False)
    date_time_to = models.DateTimeField(_("To date time"), auto_now=False, auto_now_add=False)

    # Relationship filter
    fixed_price = models.ForeignKey(FixedPrice, on_delete=models.CASCADE)

    class Meta:
        """Meta class"""

        verbose_name = "Date range"
        verbose_name_plural = "Date range's"
        ordering = ['fixed_price', 'date_time_from']
        default_related_name = 'date_ranges'


class AttributeType(ChatbootModel):

    # Filter data
    name = models.CharField(max_length=255)
    slug_name = models.SlugField(max_length=255, null=True, blank=True)

    # Relationship filter
    store = models.ForeignKey(
        "stores.Store", verbose_name=_("Store"), on_delete=models.CASCADE,
        default=None, null=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Attribute type'
        verbose_name_plural = "Attribute type's"
        default_related_name = 'attributes_type'


class Attribute(BaseRawAbstract):
    """Attributes model"""

    # Filter data
    value = models.CharField(max_length=255)

    # Relationship filter
    sku = models.ForeignKey(Skus, on_delete=models.CASCADE)
    attribute_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.sku.name}: {self.attribute_type}: {self.value}'

    class Meta:
        """Meta class"""

        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        default_related_name = 'attributes'
