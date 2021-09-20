"""Skus model."""

from slugify import slugify

# Django
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


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
        self.serializer_data = self.get_sku
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Sku"
        verbose_name_plural = "Sku's"
        default_related_name = 'skus'

    @property
    def get_sku(self):
        from chatbot_commerce.stores.models import SkuSeller
        sku_seller = SkuSeller.objects.filter(sku__pk=self.pk).values_list('serializer_data', flat=True)
        sku_dict = {
            'id': self.external_id,
            'name': self.name,
            'total_quantity': self.total_quantity,
            'is_active': self.is_active,
            'images': self.get_images,
            'attributes': self.get_attributes,
            'price': self.get_prices,
            'sellers': list(sku_seller)
        }
        return sku_dict

    @property
    def get_prices(self):
        obj = self.price.all().first()
        if obj:
            return obj.serializer_data

    @property
    def get_attributes(self):
        return list(self.attributes.all().values_list('serializer_data', flat=True))

    @property
    def get_images(self):
        return list(self.images.all().values_list('image_url', flat=True))


@receiver(post_save, sender=Skus)
def call_sku_seller_save_from_skus(sender, instance, *args, **kwargs):
    [sku_seller.save() for sku_seller in instance.sku_seller.all()]


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


@receiver(post_save, sender=Image)
def call_sku_save_from_image_for_save(sender, instance, *args, **kwargs):
    instance.sku.save()


@receiver(post_delete, sender=Image)
def call_sku_save_from_image_for_delete(sender, instance, *args, **kwargs):
    instance.sku.save()


class Price(BaseRawAbstract):
    """Price model"""

    list_price = models.BigIntegerField(_('List price'), null=True, blank=True)
    cost_price = models.BigIntegerField(_('Cost price'), null=True, blank=True)
    markup = models.BigIntegerField(_('Mark up'), null=True, blank=True)

    # Filter data
    base_price = models.BigIntegerField(_('Base price'), null=True, blank=True)

    # Relationship filter
    sku = models.ForeignKey(Skus, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_price
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = 'Price'
        verbose_name_plural = "Price's"
        ordering = ['sku', 'cost_price']
        default_related_name = 'price'

    def __str__(self):
        """Return sku price."""
        return f'sku:{self.base_price}'

    @property
    def get_price(self):
        price = {
            "base_price": self.base_price,
            "fixed_prices": list(self.fixed_prices.all().values_list('serializer_data', flat=True))
        }
        return price


@receiver(post_save, sender=Price)
def call_sku_save_from_price_for_save(sender, instance, *args, **kwargs):
    instance.sku.save()


@receiver(post_delete, sender=Price)
def call_sku_save_from_price_for_delete(sender, instance, *args, **kwargs):
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
        self.serializer_data = self.get_fixed_price
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Fixed price"
        verbose_name_plural = "Fixed price's"
        ordering = ['price', 'trade_policy_id']
        default_related_name = 'fixed_prices'

    @property
    def get_fixed_price(self):
        fixed_price = {
            "value": self.value,
            "date_ranges": list(self.date_ranges.all().values_list('serializer_data', flat=True))
        }
        return fixed_price


@receiver(post_save, sender=FixedPrice)
def call_price_save_from_fixedprice_for_save(sender, instance, *args, **kwargs):
    instance.price.save()


@receiver(post_delete, sender=FixedPrice)
def call_price_save_from_fixedprice_for_delete(sender, instance, *args, **kwargs):
    instance.price.save()


class DateRange(BaseRawAbstract):
    """Date range model"""

    # Filter data
    date_time_from = models.DateTimeField(_("From date time"), auto_now=False, auto_now_add=False)
    date_time_to = models.DateTimeField(_("To date time"), auto_now=False, auto_now_add=False)

    # Relationship filter
    fixed_price = models.ForeignKey(FixedPrice, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_date_range
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Date range"
        verbose_name_plural = "Date range's"
        ordering = ['fixed_price', 'date_time_from']
        default_related_name = 'date_ranges'

    @property
    def get_date_range(self):
        date_rage = {
            "from": self.date_time_from,
            "to": self.date_time_to
        }
        return date_rage


@receiver(post_save, sender=DateRange)
def call_fixedprice_save_from_daterange_for_save(sender, instance, *args, **kwargs):
    instance.fixed_price.save()


@receiver(post_delete, sender=DateRange)
def call_fixedprice_save_from_daterange_for_delete(sender, instance, *args, **kwargs):
    instance.fixed_price.save()


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


@receiver(post_save, sender=AttributeType)
def call_attributes_save_from_attributetype_for_save(sender, instance, *args, **kwargs):
    [attribute.save() for attribute in instance.attributes.all()]


class Attribute(BaseRawAbstract):
    """Attributes model"""

    # Filter data
    value = models.CharField(max_length=255)

    # Relationship filter
    sku = models.ForeignKey(Skus, on_delete=models.CASCADE)
    attribute_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.sku.name}: {self.attribute_type}: {self.value}'

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_attribute
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        unique_together = ['sku', 'attribute_type']
        default_related_name = 'attributes'

    @property
    def get_attribute(self):
        attribute_dict = {
            "type": self.attribute_type.name,
            "value": self.value
        }
        return attribute_dict


@receiver(post_save, sender=Attribute)
def call_sku_save_from_attribute_for_save(sender, instance, *args, **kwargs):
    instance.sku.save()


@receiver(post_delete, sender=Attribute)
def call_sku_save_from_attribute_for_delete(sender, instance, *args, **kwargs):
    instance.sku.save()
