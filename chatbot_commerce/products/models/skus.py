"""Skus model."""

from slugify import slugify

# Django
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver


# utilities
from chatbot_commerce.utils.models import ChatbootModel
from django.utils.translation import gettext as _


class Skus(ChatbootModel):
    """Store departmentss"""

    sku_id = models.CharField(
        'Sku ID',
        max_length=10
    )

    sku_name = models.CharField(
        'name sku',
        max_length=255,
        null=True,
        blank=True
    )

    total_quantity = models.CharField(
        'Quantity sku',
        max_length=255,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        'Active sku',
        default=False,
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

    is_kit = models.BooleanField(
        'sku is kit',
        default=False,
        null=True,
        blank=True
    )

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

    reference_stock_id = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )

    is_inventoried = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )

    is_transported = models.BooleanField(
        default=False,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        to='products.Product',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='skus'
    )

    sku_json = models.JSONField(
        'Complete sku data',
        null=True,
        blank=True
    )

    serializer_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        """Return sku id."""
        return f'sku:{self.sku_name}'

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_sku
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Sku"
        verbose_name_plural = "Sku's"

    @property
    def get_sku(self):
        sku_dict = {
            'id': self.sku_id,
            'name': self.sku_name,
            'total_quantity': self.total_quantity,
            'is_active': self.is_active,
            'images': self.get_images,
            'attributes': self.get_attributes,
            'price': self.get_prices
        }
        return sku_dict

    @property
    def get_prices(self):
        obj = self.price.all().order_by().first()
        if obj:
            return obj.serializer_data

    @property
    def get_attributes(self):
        return list(self.attributes.all().order_by().values_list('serializer_data', flat=True))

    @property
    def get_images(self):
        return list(self.sku_images.all().order_by().values_list('image_url', flat=True))


class Image(ChatbootModel):
    """Image model"""

    image_id = models.BigIntegerField(_("ID"), null=True, blank=True)
    archive_id = models.BigIntegerField(_("Archive ID"), null=True, blank=True)
    sku = models.ForeignKey("products.Skus", on_delete=models.CASCADE, related_name='sku_images')
    name = models.CharField(_("Name"), max_length=500)
    is_main = models.BooleanField(_("Main image"), null=True)
    label = models.CharField(_("Label"), max_length=50, null=True, blank=True)
    image_url = models.URLField(_("Image url"), max_length=2000, null=True, blank=True)

    class Meta:
        """Meta class"""

        verbose_name = 'Image'
        verbose_name_plural = "Image's"
        ordering = ['sku_id', 'image_id']


@receiver(pre_save, sender=Image)
def create_image_url(sender, instance, *args, **kwargs):
    try:
        store_name = instance.sku.product.store.name
        print(store_name)
    except Exception as message:
        error = {
            'message': message,
            'instance': instance,
            'sku': instance.sku,
            'product': instance.sku.product,
            'sku_id': instance.sku.pk
        }
        raise Exception(error)
    instance.image_url = f'https://{store_name}.vteximg.com.br/arquivos/ids/{instance.archive_id}/{instance.name}.jpg'


@receiver(post_save, sender=Image)
def call_sku_save_from_image_for_save(sender, instance, *args, **kwargs):
    instance.sku.save()


@receiver(post_delete, sender=Image)
def call_sku_save_from_image_for_delete(sender, instance, *args, **kwargs):
    instance.sku.save()


class Price(ChatbootModel):
    """Price model"""

    sku = models.ForeignKey(Skus, on_delete=models.CASCADE, related_name='price')
    list_price = models.BigIntegerField(_('List price'), null=True, blank=True)
    cost_price = models.BigIntegerField(_('Cost price'), null=True, blank=True)
    markup = models.BigIntegerField(_('Mark up'), null=True, blank=True)
    base_price = models.BigIntegerField(_('Base price'), null=True, blank=True)
    serializer_data = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_price
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = 'Price'
        verbose_name_plural = "Price's"
        ordering = ['sku', 'cost_price']

    def __str__(self):
        """Return sku price."""
        return f'sku:{self.base_price}'

    @property
    def get_price(self):
        price = {
            "base_price": self.base_price,
            "fixed_prices": list(self.fixed_prices.all().order_by().values_list('serializer_data', flat=True))
        }
        return price


@receiver(post_save, sender=Price)
def call_sku_save_from_price_for_save(sender, instance, *args, **kwargs):
    instance.sku.save()


@receiver(post_delete, sender=Price)
def call_sku_save_from_price_for_delete(sender, instance, *args, **kwargs):
    instance.sku.save()


class FixedPrice(ChatbootModel):
    """Fixed price model"""

    price = models.ForeignKey(Price, on_delete=models.CASCADE, related_name='fixed_prices')
    trade_policy_id = models.CharField(_('Trade porlice ID'), max_length=50)
    value = models.BigIntegerField(_('Value'), null=True, blank=True)
    list_price = models.BigIntegerField(_('List price'), null=True, blank=True)
    min_quantity = models.IntegerField(_('Minimun quantity'), null=True, blank=True)
    serializer_data = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_fixed_price
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Fixed price"
        verbose_name_plural = "Fixed price's"
        ordering = ['price', 'trade_policy_id']

    @property
    def get_fixed_price(self):
        fixed_price = {
            "value": self.value,
            "date_ranges": list(self.date_ranges.all().order_by().values_list('serializer_data', flat=True))
        }
        return fixed_price


@receiver(post_save, sender=FixedPrice)
def call_price_save_from_fixedprice_for_save(sender, instance, *args, **kwargs):
    instance.price.save()


@receiver(post_delete, sender=FixedPrice)
def call_price_save_from_fixedprice_for_delete(sender, instance, *args, **kwargs):
    instance.price.save()


class DateRange(ChatbootModel):
    """Date range model"""

    fixed_price = models.ForeignKey(FixedPrice, on_delete=models.CASCADE, related_name="date_ranges")
    date_time_from = models.DateTimeField(_("From date time"), auto_now=False, auto_now_add=False)
    date_time_to = models.DateTimeField(_("To date time"), auto_now=False, auto_now_add=False)
    serializer_data = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_date_range
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Date range"
        verbose_name_plural = "Date range's"
        ordering = ['fixed_price', 'date_time_from']

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

    store = models.ForeignKey(
        "stores.Store", verbose_name=_("Store"), on_delete=models.CASCADE,
        related_name='attributes_type', default=None, null=True
    )
    name = models.CharField(max_length=255)
    slug_name = models.SlugField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)


@receiver(post_save, sender=AttributeType)
def call_attributes_save_from_attributetype_for_save(sender, instance, *args, **kwargs):
    [attribute.save() for attribute in instance.attributes.all().order_by()]


class Attribute(ChatbootModel):
    """Attributes model"""

    sku = models.ForeignKey(Skus, on_delete=models.CASCADE, related_name='attributes')
    attribute_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE, related_name='attributes')
    value = models.CharField(max_length=255)
    serializer_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.sku.sku_name}: {self.attribute_type}: {self.value}'

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_attribute
        return super().save(*args, **kwargs)

    class Meta:
        """Meta class"""

        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        unique_together = ['sku', 'attribute_type']

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
