"""Skus model."""

from slugify import slugify

# Django
from django.db import models
from django.contrib.postgres.search import SearchVectorField

# utilities
from chatbot_commerce.utils.models import ChatbootModel, BaseAbstract, BaseRawAbstract
from django.utils.translation import gettext as _


class Skus(BaseAbstract):
    """Store departmentss"""

    # Filter data
    is_active = models.BooleanField(
        'Active sku',
        default=False, null=True, blank=True,
    )
    is_inventoried = models.BooleanField(
        default=False, null=True, blank=True
    )
    total_quantity = models.PositiveBigIntegerField(
        'Quantity sku',
        default=0, blank=True
    )
    # search_attributes = models.TextField(_("Attributes search"), blank=True, null=True)
    search = models.TextField(
        _("Search"),
        blank=True, null=True
    )
    search_vector = SearchVectorField(
        _("Search vector"),
        blank=True, null=True
    )

    is_transported = models.BooleanField(
        default=False, null=True, blank=True
    )
    is_kit = models.BooleanField(
        'sku is kit',
        default=False, null=True, blank=True
    )

    # Relationship filter
    product = models.ForeignKey(
        to='stores.Product', on_delete=models.CASCADE,
        null=True, blank=True,
    )
    sales_channels = models.ManyToManyField(
        "stores.SaleChannel", verbose_name=_("Sales channel's")
    )

    # Extra data
    comercial_condition_id = models.CharField(
        max_length=100,
        null=True, blank=True
    )
    manufacter_code = models.CharField(
        max_length=100,
        null=True, blank=True
    )
    ref_id = models.CharField(
        'Reference id',
        max_length=100,
        null=True, blank=True
    )
    packaged_height = models.CharField(
        max_length=50,
        null=True, blank=True
    )
    packaged_length = models.CharField(
        max_length=50,
        null=True, blank=True
    )
    packaged_width = models.CharField(
        max_length=50,
        null=True, blank=True
    )
    packaged_weight = models.CharField(
        'Packaged weight Kg',
        max_length=50,
        null=True, blank=True
    )
    reference_stock_id = models.BooleanField(
        default=False, null=True, blank=True
    )

    sku_price = models.FloatField(verbose_name='Price', null=True, blank=True)

    def __str__(self):
        """Return sku id."""
        return f'{self.name}'

    @property
    def get_serializer_data(self):
        array_sku_seller = list(self.sku_seller.values_list('seller__seller_id', flat=True))
        if array_sku_seller:
            seller = array_sku_seller[0]
        else:
            seller = None

        try:
            price = self.price
            if price:
                price = price.serializer_data
                self.sku_price = price['base_price']
        except (Exception):
            price = 0.0
        # else:
        #     price = None

        self.serializer_data = {
            'sku_id': self.external_id,
            'seller_id': seller,
            'sku_name': self.name,
            'total_quantity': self.total_quantity,
            'images': list(Image.objects.filter(skus=self.pk).values_list('image_url', flat=True)),
            'price': price,
            'attributes': list(Attribute.objects.filter(skus=self.pk).values('value', attribute_name=models.F('attribute_type__name'))),
            'is_active': self.is_active
        }
        return self.save()

    class Meta:
        verbose_name = "Sku"
        verbose_name_plural = "Sku's"
        default_related_name = 'skus'
        # indexes = [models.Index(fields=['is_active', 'external_id', 'total_quantity', 'sku_price', 'search_vector'])]
        indexes = [models.Index(fields=['is_active', 'external_id'])]


class Image(ChatbootModel):
    """Image model"""

    # Filter data
    name = models.CharField(
        _("Name"),
        max_length=500,
        null=True, blank=True
    )
    image_id = models.CharField(
        _("Image external id"),
        max_length=50,
        null=True, blank=True
    )
    position = models.IntegerField(null=True, blank=True)
    width = models.BigIntegerField(null=True, blank=True)
    height = models.BigIntegerField(null=True, blank=True)

    # Relationship filter
    store = models.ForeignKey(
        "stores.Store", verbose_name=_("Store"), on_delete=models.CASCADE
    )
    products = models.ManyToManyField(
        "stores.Product", verbose_name=_('Products'), related_name='product_images'
    )
    skus = models.ManyToManyField(
        "stores.Skus", verbose_name=_('Skus')
    )

    # Url data
    image_url = models.URLField(
        _("Image url"),
        max_length=2000,
        null=True, blank=True
    )

    class Meta:
        """Meta class"""

        verbose_name = 'Image'
        verbose_name_plural = "Image's"
        unique_together = ('image_id', 'store', 'name', 'image_url')
        default_related_name = 'images'


class Price(BaseRawAbstract):
    """Price model"""

    list_price = models.BigIntegerField(
        _('List price'),
        null=True, blank=True
    )
    cost_price = models.BigIntegerField(
        _('Cost price'),
        null=True, blank=True
    )
    markup = models.BigIntegerField(
        _('Mark up'),
        null=True, blank=True
    )

    # Filter data
    base_price = models.FloatField(
        _('Base price'),
        default=0.0, blank=True
    )

    # Relationship filter
    sku = models.OneToOneField("stores.Skus", verbose_name=_("Sku"), on_delete=models.CASCADE)

    class Meta:
        """Meta class"""

        verbose_name = 'Price'
        verbose_name_plural = "Price's"
        default_related_name = 'price'

    def save(self, *args, **kwargs):
        try:
            fixed_prices = list(self.fixed_prices.values_list('serializer_data', flat=True))
        except (Exception):
            fixed_prices = []
        self.serializer_data = {
            'base_price': self.base_price,
            'fixed_prices': fixed_prices
        }
        return super().save(*args, **kwargs)

    def __str__(self):
        """Return sku price."""
        return f'sku:{self.base_price}'


class FixedPrice(BaseRawAbstract):
    """Fixed price model"""

    # Filter data
    trade_policy_id = models.CharField(
        _('Trade porlice ID'),
        max_length=50
    )
    value = models.FloatField(
        _('Value'),
        null=True, blank=True
    )
    list_price = models.BigIntegerField(
        _('List price'),
        null=True, blank=True
    )
    min_quantity = models.IntegerField(
        _('Minimun quantity'),
        null=True, blank=True
    )

    # Relationship filter
    price = models.ForeignKey(
        'stores.Price', on_delete=models.CASCADE
    )

    date_range = models.OneToOneField("stores.DateRange", verbose_name=_("Date range"), on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            date_ranges = {'date_time_from': self.date_range.date_time_from, 'date_time_to': self.date_range.date_time_to} if self.date_range else None
        except (Exception):
            date_ranges = {}
        self.serializer_data = {
            'value': self.value,
            'date_ranges': date_ranges
        }
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Fixed price"
        verbose_name_plural = "Fixed price's"
        default_related_name = 'fixed_prices'


class DateRange(BaseRawAbstract):
    """Date range model"""

    # Filter data
    date_time_from = models.DateTimeField(
        _("From date time"),
        auto_now=False, auto_now_add=False
    )
    date_time_to = models.DateTimeField(
        _("To date time"),
        auto_now=False, auto_now_add=False
    )

    class Meta:
        """Meta class"""

        verbose_name = "Date range"
        verbose_name_plural = "Date range's"


class AttributeType(ChatbootModel):

    # Filter data
    name = models.CharField(
        max_length=255
    )
    slug_name = models.SlugField(
        max_length=255,
        null=True, blank=True
    )

    # Relationship filter
    store = models.ForeignKey(
        "stores.Store", verbose_name=_("Store"), on_delete=models.CASCADE,
        default=None, null=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        self.name = self.name.strip().capitalize()
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Attribute type'
        verbose_name_plural = "Attribute type's"
        unique_together = ('name', 'store',)
        default_related_name = 'attributes_type'


class Attribute(BaseRawAbstract):
    """Attributes model"""

    # Filter data
    value = models.CharField(
        max_length=255
    )

    # Relationship filter
    skus = models.ManyToManyField(
        'stores.Skus', verbose_name=_("Skus")
    )
    attribute_type = models.ForeignKey(
        'stores.AttributeType', on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.attribute_type}: {self.value}'

    class Meta:
        """Meta class"""

        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        unique_together = ('attribute_type', 'value',)
        default_related_name = 'attributes'
