"""Sku model."""
from slugify import slugify

# Django
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

# utilities
from chatbot_commerce.utils.models import ChatbootModel, BaseAbstract, BaseRawAbstract, super_save
from django.utils.translation import gettext as _

# Models
from chatbot_commerce.stores.models.stores import UpdateModels


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

    # Serializers
    sellers_id = ArrayField(base_field=models.CharField(max_length=100), default=list, editable=False)
    images_url = ArrayField(base_field=models.CharField(max_length=100), default=list, editable=False)
    sku_price = models.FloatField(verbose_name='Price', null=True, blank=True, editable=False)
    attributes_data = ArrayField(base_field=models.JSONField(null=True, blank=True), default=list, editable=False)

    def __init__(self: "Sku", *args, **kwargs) -> None:
        """Initialize instance."""

        self.old_sellers = self.sellers
        self.old_images = self.images
        self.old_price = self.price
        self.old_attributes = self.attributes

        super().__init__(*args, **kwargs)

    def __str__(self):
        """Return sku name, from sku."""

        return f'{self.name}'

    def save(self, *args, **kwargs) -> None:
        """Save instance."""

        if self.old_sellers != self.sellers:
            return self.set_sellers()
        if self.old_images != self.images:
            return self.set_images()
        if self.old_price != self.price:
            return self.set_price()
        if self.old_attributes != self.attributes:
            return self.set_attributes()

        super().save(*args, **kwargs)

    @property
    def set_sellers(self):
        """Set sellers."""

        self.sellers_id = list(self.sku_seller.values_list('seller__seller_id', flat=True))

        super().save()

    @property
    def set_images(self):
        """Set images."""

        self.images_url = list(self.sku_images.values_list('image_url', flat=True))

        super().save()

    @property
    def set_price(self):
        """Set price."""

        self.sku_price = self.price.base_price if self.price else 0.0

        super().save()

    @property
    def set_attributes(self):
        """Set attributes."""

        self.attributes_data = list(Attribute.objects.filter(skus=self.pk).values('value', attribute_name=models.F('attribute_type__name')))

        super().save()

    class Meta:
        verbose_name = "Sku"
        verbose_name_plural = "Sku's"
        default_related_name = 'skus'
        # indexes = [models.Index(fields=['is_active', 'external_id', 'total_quantity', 'sku_price', 'search_vector'])]
        indexes = [models.Index(fields=['is_active', 'external_id'])]


@receiver(post_save, sender=Sku)
def update_sku_data(sender, instance, **kwargs):
    """Update sku data."""

    if instance.firts_time:
        if instance.sku_seller:
            instance.set_sellers()
        if instance.sku_images:
            instance.set_images()
        if instance.price:
            instance.set_price()
        if instance.attributes:
            instance.set_attributes()
        super_save(instance)


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
        "stores.Sku", verbose_name=_('Skus')
    )

    # Url data
    image_url = models.URLField(
        _("Image url"),
        max_length=2000,
        null=True, blank=True
    )

    def __init__(self: "Image", *args, **kwargs) -> None:
        """Initialize instance."""

        self.old_image_url = self.image_url

        super().__init__(*args, **kwargs)

    def __str__(self):
        """Return image url, from image."""

        return f'{self.image_url}'

    def save(self, *args, **kwargs) -> None:
        """Save instance."""

        self.update_father_serializer_data = self.old_image_url != self.image_url

        super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = 'Image'
        verbose_name_plural = "Image's"
        unique_together = ('image_id', 'store', 'name', 'image_url')
        default_related_name = 'images'


@receiver(post_save, sender=Image)
def update_image_serializer_data(sender, instance, *args, **kwargs):
    """Update image serializer data."""

    if (instance.update_father_serializer_data or instance.first_time) and (instance.skus or instance.products):
        if instance.skus:
            set(map(lambda sku: UpdateModels.objects.get_or_create(model_name='Sku', function_name='set_images', primary_key=sku), instance.skus))
        if instance.products:
            set(map(lambda product: UpdateModels.objects.get_or_create(model_name='Product', function_name='set_images', primary_key=product), instance.products))
        super_save(instance)


@receiver(post_delete, sender=Image)
def delete_image_in_serializer_data(sender, instance, *args, **kwargs):
    """Delete image in serializer data."""

    if instance.skus:
        set(map(lambda sku: UpdateModels.objects.get_or_create(model_name='Sku', function_name='set_images', primary_key=sku), instance.skus))
    if instance.products:
        set(map(lambda product: UpdateModels.objects.get_or_create(model_name='Product', function_name='set_images', primary_key=product), instance.products))


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

    def __init__(self: "Price", *args, **kwargs) -> None:
        """Initialize instance."""

        self.old_base_price = self.base_price

        self.old_fixed_prices = self.fixed_prices
        self.old_sku = self.sku

        super().__init__(*args, **kwargs)

    def __str__(self):
        """Return base price, from price."""

        return f'sku:{self.base_price}'

    def save(self, *args, **kwargs) -> None:
        """Save price."""

        if self.old_fixed_prices != self.fixed_prices:
            return self.set_fixed_prices()

        self.update_father_serializer_data = self.old_base_price != self.base_price or self.old_sku != self.sku

        super().save(*args, **kwargs)

    @property
    def set_fixed_prices(self):
        """Set fixed prices."""

        self.fixed_prices_data = list(self.fixed_prices.values('value', date_range=models.F('date_range_data')))
        self.update_father_serializer_data = True

        super().save()

    class Meta:
        """Meta class"""

        verbose_name = 'Price'
        verbose_name_plural = "Price's"
        default_related_name = 'price'


@receiver(post_save, sender=Price)
def update_price_serializer_data(sender, instance, *args, **kwargs):
    """Update price serializer data."""

    if (instance.update_father_serializer_data or instance.first_time) and instance.sku:
        instance.sku.set_price
        super_save(instance)


@receiver(post_delete, sender=Price)
def delete_price_in_serializer_data(sender, instance, *args, **kwargs):
    """Delete price in serializer data."""

    if instance.sku:
        instance.sku.set_price


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
    date_rage_data = models.JSONField(null=True, blank=True, editable=False)

    def __init__(self: "FixedPrice", *args, **kwargs) -> None:
        """Initialize instance."""

        self.old_value = self.value

        self.old_date_range = self.date_range
        self.old_price = self.price

        super().__init__(*args, **kwargs)

    def __str__(self):
        """Return value, from fixed price."""

        return f'{self.value}'

    def save(self, *args, **kwargs):
        """Save instance."""

        if self.old_date_range != self.date_range:
            return self.set_date_range()

        self.update_father_serializer_data = self.old_value != self.value or \
            self.old_date_range != self.date_range or self.old_price != self.price

        super().save(*args, **kwargs)

    @property
    def set_date_range(self):
        """Set date range."""

        self.date_rage_data = self.date_range.serializer_data if self.date_range else dict()
        self.update_father_serializer_data = True

        super().save()

    class Meta:
        """Meta class"""

        verbose_name = "Fixed price"
        verbose_name_plural = "Fixed price's"
        default_related_name = 'fixed_prices'


@receiver(post_save, sender=FixedPrice)
def update_fixed_price_serializer_data(sender, instance, *args, **kwargs):
    """Update fixed price serializer data."""

    if (instance.update_father_serializer_data or instance.first_time) and instance.price:
        UpdateModels.objects.get_or_create(model_name='Price', function_name='set_fixed_prices', primary_key=instance.price)
        super_save(instance)


@receiver(post_delete, sender=FixedPrice)
def delete_fixed_price_in_serializer_data(sender, instance, *args, **kwargs):
    """Delete fixed price in serializer data."""

    if instance.price:
        UpdateModels.objects.get_or_create(model_name='Price', function_name='set_fixed_prices', primary_key=instance.price)


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

    def __init__(self: "DateRange", *args, **kwargs) -> None:
        """Initialize instance."""

        self.old_date_time_from = self.date_time_from
        self.old_date_time_to = self.date_time_to
        self.old_fixed_price = self.fixed_price

        super().__init__(*args, **kwargs)

    def __str__(self):
        """Return date range, from date range."""

        return f'{self.date_time_from} - {self.date_time_to}'

    def save(self, *args, **kwargs):
        """Save instance."""

        self.update_father_serializer_data = self.old_date_time_from != self.date_time_from or \
            self.old_date_time_to != self.date_time_to or self.old_fixed_price != self.fixed_price
        super().save(*args, **kwargs)

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


@receiver(post_save, sender=DateRange)
def update_date_range_serializer_data(sender, instance, *args, **kwargs):
    """Update date range serializer data."""

    if (instance.update_father_serializer_data or instance.first_time) and instance.fixed_price:
        instance.fixed_price.set_date_range
        super_save(instance)


@receiver(post_delete, sender=DateRange)
def delete_date_range_in_serializer_data(sender, instance, *args, **kwargs):
    """Delete date range in serializer data."""

    if instance.fixed_price:
        instance.fixed_price.set_date_range


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

    def __init__(self: "AttributeType", *args, **kwargs) -> None:
        """Initialize instance."""

        self.old_name = self.name

        self.old_attributes = self.attributes

        super().__init__(*args, **kwargs)

    def __str__(self):
        """Return name, from attribute type."""

        return self.name

    def save(self, *args, **kwargs):
        """Save instance."""

        self.update_sons_serializer_data = self.old_name != self.name or self.old_attributes != self.attributes
        if self.old_name != self.name or self.slug_name is None:
            self.name = self.name.strip().capitalize()
            self.slug_name = slugify(self.name, separator="_")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Attribute type'
        verbose_name_plural = "Attribute type's"
        unique_together = ('name', 'store',)
        default_related_name = 'attributes_type'


@receiver(post_save, sender=AttributeType)
def update_attribute_type_serializer_data(sender, instance, *args, **kwargs):
    """Update attribute type serializer data."""

    if (instance.update_sons_serializer_data or instance.first_time) and instance.attributes:
        set(
            map(
                lambda attribute:
                set(
                    map(
                        lambda sku: UpdateModels.objects.get_or_create(model_name='Sku', function_name='set_attributes', primary_key=sku),
                        attribute.skus
                    )
                ),
                instance.attributes
            )
        )
        super_save(instance)


@receiver(post_delete, sender=AttributeType)
def delete_attribute_type_in_serializer_data(sender, instance, *args, **kwargs):
    """Delete attribute type in serializer data."""

    if instance.attributes:
        set(
            map(
                lambda attribute:
                set(
                    map(
                        lambda sku: UpdateModels.objects.get_or_create(model_name='Sku', function_name='set_attributes', primary_key=sku),
                        attribute.skus
                    )
                ),
                instance.attributes
            )
        )


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

    def __init__(self: "Attribute", *args, **kwargs) -> None:

        self.old_value = self.value

        self.old_attribute_type = self.attribute_type
        self.old_skus = self.skus

        super().__init__(*args, **kwargs)

    def __str__(self):
        """Return type: value, from attribute."""

        return f'{self.attribute_type}: {self.value}'

    def save(self, *args, **kwargs):
        """Save instance."""

        self.update_father_serializer_data = self.old_value != self.value or \
            self.old_attribute_type != self.attribute_type or \
            self.old_skus != self.skus

        super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        unique_together = ('attribute_type', 'value',)
        default_related_name = 'attributes'


@receiver(post_save, sender=Attribute)
def update_attribute_serializer_data(sender, instance, *args, **kwargs):
    """Update attribute serializer data."""

    if (instance.update_father_serializer_data or instance.first_time) and instance.attribute_type and instance.skus:
        set(map(lambda sku: UpdateModels.objects.get_or_create(model_name='Sku', function_name='set_attributes', primary_key=sku), instance.skus))
        super_save(instance)


@receiver(post_delete, sender=Attribute)
def delete_attribute_in_serializer_data(sender, instance, *args, **kwargs):
    """Delete attribute in serializer data."""

    if instance.skus:
        set(map(lambda sku: UpdateModels.objects.get_or_create(model_name='Sku', function_name='set_attributes', primary_key=sku), instance.skus))
