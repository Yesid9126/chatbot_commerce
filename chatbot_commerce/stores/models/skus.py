"""Sku model."""
from slugify import slugify

# Django
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField

# utilities
from chatbot_commerce.utils.models import ChatbootModel, BaseAbstract, BaseRawAbstract
from django.utils.translation import gettext as _


class Sku(BaseAbstract):
    """Store departmentss"""

    # Filter data
    is_active = models.BooleanField(
        'Active sku',
        default=False, null=True, blank=True,
    )
    is_inventoried = models.BooleanField(
        default=False, null=True, blank=True
    )
    total_quantity = models.BigIntegerField(
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
    packaged_widtht = models.CharField(
        max_length=50,
        null=True, blank=True
    )
    packaged_weight_unit = models.CharField(
        'Packaged weight unit',
        max_length=50,
        null=True, blank=True
    )
    reference_stock_id = models.BooleanField(
        default=False, null=True, blank=True
    )

    # Serializers
    sellers_id = ArrayField(base_field=models.CharField(max_length=100), default=list, editable=False)
    images_url = ArrayField(base_field=models.CharField(max_length=100), default=list, editable=False)
    sku_price = models.FloatField(verbose_name='Price', null=True, blank=True, editable=False)
    price_data = models.JSONField(verbose_name='Data price', null=True, blank=True, editable=False)
    attributes_data = ArrayField(base_field=models.JSONField(null=True, blank=True), default=list, editable=False)

    def __str__(self):
        """Return sku name, from sku."""

        return f'{self.name}'

    @property
    def update_serializer_data(self):
        self.set_sellers
        self.set_images
        self.set_price
        self.set_attributes
        super().save(update_fields=['sellers_id', 'images_url', 'sku_price', 'price_data', 'attributes_data'])

    @property
    def set_sellers(self):
        """Set sellers."""

        self.sellers_id = list(self.sku_seller.values_list('seller__seller_id', flat=True))

    @property
    def set_images(self):
        """Set images."""

        self.images_url = list(self.images.values_list('image_url', flat=True))

    @property
    def set_price(self):
        """Set price."""

        self.sku_price = self.price.base_price if hasattr(self, 'price') else 0.0
        self.price_data = {
            'base_price': self.price.base_price,
            'fixed_prices': self.price.fixed_prices_data,
        } if hasattr(self, 'price') else dict()

    @property
    def set_attributes(self):
        """Set attributes."""

        self.attributes_data = list(Attribute.objects.filter(skus=self.pk).values('value', attribute_name=models.F('attribute_type__name')))

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

    product = models.ForeignKey(
        "stores.Product", verbose_name=_('Products'), related_name='product_images',
        on_delete=models.CASCADE, default=None, null=True, blank=True
    )
    sku = models.ForeignKey(
        "stores.Sku", verbose_name=_('Skus'),
        on_delete=models.SET_NULL, default=None, null=True, blank=True
    )

    # Url data
    image_url = models.URLField(
        _("Image url"),
        max_length=2000,
        null=True, blank=True
    )

    def __str__(self):
        """Return image url, from image."""

        return f'{self.image_url}'

    class Meta:
        """Meta class"""

        verbose_name = 'Image'
        verbose_name_plural = "Image's"

        constraints = [
            models.UniqueConstraint(fields=['image_id', 'name', 'image_url', 'sku', 'product'], name='unique_image'),
        ]

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
    sku = models.OneToOneField("stores.Sku", verbose_name=_("Sku"), on_delete=models.CASCADE)

    # Serializers
    fixed_prices_data = ArrayField(base_field=models.JSONField(blank=True, null=True), default=list, editable=False)

    def __str__(self):
        """Return base price, from price."""

        return f'sku:{self.base_price}'

    @property
    def set_fixed_prices(self):
        """Set fixed prices."""

        self.fixed_prices_data = list(self.fixed_prices.values('value', date_ranges=models.F('date_range_data')))
        super().save(update_fields=['fixed_prices_data'])

    class Meta:
        """Meta class"""

        verbose_name = 'Price'
        verbose_name_plural = "Price's"
        default_related_name = 'price'


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

    date_range = models.OneToOneField("stores.DateRange", verbose_name=_("Date range"), on_delete=models.SET_NULL, null=True, blank=True, related_name='fixed_price')

    # Serializers
    date_range_data = models.JSONField(null=True, blank=True, editable=False, default=list)

    def __str__(self):
        """Return value, from fixed price."""

        return f'{self.value}'

    @property
    def set_date_range(self):
        """Set date range."""
        if self.date_range:
            self.date_range_data = [self.date_range.serializer_data]
            super().save(update_fields=['date_range_data'])

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

    def __str__(self):
        """Return date range, from date range."""

        return f'{self.date_time_from} - {self.date_time_to}'

    @property
    def serializer_data(self, update_father_serializer_data: bool = True) -> None:
        """Get serializer data."""

        return {
            'date_time_from': self.date_time_from,
            'date_time_to': self.date_time_to
        }

    class Meta:
        """Meta class"""

        verbose_name = "Date range"
        verbose_name_plural = "Date range's"


class AttributeType(ChatbootModel):
    """Attribute type model"""

    # Filter data
    name = models.CharField(
        max_length=255
    )
    slug_name = models.SlugField(
        max_length=255,
        null=True, blank=True,
        editable=False
    )

    # Relationship filter
    store = models.ForeignKey(
        "stores.Store", verbose_name=_("Store"), on_delete=models.CASCADE,
        default=None, null=True
    )

    def __str__(self):
        """Return name, from attribute type."""

        return self.name

    def save(self, *args, **kwargs):
        """Save instance."""

        if not self.slug_name and self.name:
            if not self.pk:
                self.name = self.name.strip().capitalize()
            self.slug_name = slugify(self.name, separator="_")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Attribute type'
        verbose_name_plural = "Attribute type's"

        constraints = [
            models.UniqueConstraint(fields=['name', 'store'], name='unique_attribute_type'),
        ]

        default_related_name = 'attributes_type'


class Attribute(BaseRawAbstract):
    """Attributes model"""

    # Filter data
    value = models.CharField(
        max_length=255
    )

    # Relationship filter
    skus = models.ManyToManyField(
        'stores.Sku', verbose_name=_("Skus")
    )
    attribute_type = models.ForeignKey(
        'stores.AttributeType', on_delete=models.CASCADE
    )

    def __str__(self):
        """Return type: value, from attribute."""

        return f'{self.attribute_type}: {self.value}'

    class Meta:
        """Meta class"""

        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        constraints = [
            models.UniqueConstraint(fields=['attribute_type', 'value'], name='unique_attribute'),
        ]
        default_related_name = 'attributes'
