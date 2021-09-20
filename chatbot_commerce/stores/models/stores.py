"""Stores model."""

# Raw
from slugify import slugify

# Django
from django.db import models

# Celery
from django_celery_beat.models import PeriodicTask, CrontabSchedule

# utilities
from chatbot_commerce.utils.models import ChatbootModel
from django.utils.translation import gettext as _
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import requests


class Store(ChatbootModel):
    """Stores model."""

    # info filter
    store_type = models.CharField(_("Type of store"), max_length=500)
    name = models.CharField(_("Name of store"), max_length=255)
    slug_name = models.SlugField(max_length=50, null=True, blank=True)
    url_enviroment = models.CharField(_("Url enviroment"), max_length=500, blank=True, null=True)

    # Task manage
    sync_status = models.BooleanField(_("Task begun Finish"), default=False)
    updating_elements_status = models.BooleanField(_("Task updating store elements"), default=False)
    creating_elements_status = models.BooleanField(_("Task creating store elments"), default=False)

    # Request information
    domain = models.CharField(_("Domain of store"), max_length=500, blank=True, null=True)
    status = models.BooleanField(_("Valid connection"), default=False)
    api_key = models.CharField(max_length=500)
    api_token = models.CharField(max_length=500)
    last_page = models.BigIntegerField(_("Last page get of skus"), default=0, blank=True, null=True)

    # Filter manage
    disable_filters = models.BooleanField(_("Disable filters"), default=False)
    apply_filter_enable_products = models.BooleanField(_("Enable products"), default=True)
    apply_filter_enable_skus = models.BooleanField(_("Enable skus"), default=True)
    apply_filter_price = models.BooleanField(_("Valid price"), default=True)
    apply_filter_image = models.BooleanField(_("Valid image"), default=True)

    def __str__(self):
        """Return store name."""
        return f'Store:{self.name}'

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"

    @property
    def headers(self):
        headers = {
            "X-VTEX-API-AppKey": f"{self.api_key}",
            "X-VTEX-API-AppToken": f"{self.api_token}"
        }
        return headers

    @property
    def urls(self):
        if self.store_type == 'Vtex':
            urls = {
                "base_url": f'https://{self.name}.{self.url_enviroment}',
                "base_price_url": f'https://api.vtex.com/{self.name}',
                "status_url": f'https://{self.name}.{self.url_enviroment}/catalog_system/pvt/brand/list'
            }
        return urls

    def save(self, *args, **kwargs):
        if self.disable_filters:
            self.apply_filter_enable_products = False
            self.apply_filter_enable_skus = False
            self.apply_filter_image = False
            self.apply_filter_price = False
        try:
            r = requests.get(url=self.urls["status_url"], headers=self.headers, timeout=1000)
            if r.status_code in [requests.codes.ok]:
                self.status = True
            else:
                self.status = False
        except Exception:
            self.status = False
        self.slug_name = slugify(self.name, separator="_")
        return super().save(*args, **kwargs)


@receiver(post_save, sender=Store)
def execute_task(sender, instance, *args, **kwargs):
    if instance.status is True and instance.sync_status is False:
        from chatbot_commerce.products.tasks import store_begining
        store_begining.s(store=instance.pk).apply_async(countdown=5)

    if instance.sync_status is True:
        try:
            every_1, _ = CrontabSchedule.objects.get_or_create(day_of_week='*', hour=1, minute=0)
            every_1_30, _ = CrontabSchedule.objects.get_or_create(day_of_week='*', hour=1, minute=30)
            task_instance, _ = PeriodicTask.objects.get_or_create(name=f'{instance.name} create & new', task='principal_periodic_task', defaults=dict(crontab=every_1, kwargs='{"store": "%s"}' % (instance.pk)))
            task_instance, _ = PeriodicTask.objects.get_or_create(name=f'{instance.name} update', task='update_periodic_task', defaults=dict(crontab=every_1_30, kwargs='{"store": "%s"}' % (instance.pk)))
        except Exception as message:
            print(message)

    if instance.status is False or instance.sync_status is False:
        PeriodicTask.objects.filter(name=f'{instance.name} create & new', task='principal_periodic_task').delete()
        PeriodicTask.objects.filter(name=f'{instance.name} update', task='update_periodic_task').delete()


@receiver(post_delete, sender=Store)
def delete_task(sender, instance, *args, **kwargs):
    PeriodicTask.objects.filter(name=f'{instance.name} create & new', task='principal_periodic_task').delete()
    PeriodicTask.objects.filter(name=f'{instance.name} update', task='update_periodic_task').delete()


class SaleChannel(ChatbootModel):
    """Trade policy model."""

    # Filter data
    name = models.CharField(_("Name of sale channel"), max_length=500)
    slug_name = models.SlugField(max_length=50, null=True, blank=True)
    external_id = models.BigIntegerField(_("Sale Channel or Trade policy id"))
    is_active = models.BooleanField(_("Status"), default=False)

    # Relationship filter
    store = models.ForeignKey("Store", verbose_name=_("Store"), on_delete=models.CASCADE)
    sellers = models.ManyToManyField("Seller", verbose_name=_("Sellers"))

    # Raw data
    raw_json = models.JSONField(_("Raw data"))

    # Hack to db queries
    serializer_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        """Return store name."""
        return f'{self.store.name.capitalize()}: sale channel = {self.name}, ID = {self.external_id}'

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        self.serializer_data = self.get_sale_channel
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Sale Channel"
        verbose_name_plural = "Sales Channel"
        default_related_name = 'sales_channel'

    @property
    def get_sale_channel(self):
        sc_dict = {
            'id': self.external_id,
            'name': self.name,
            'is_active': self.is_active
        }
        return sc_dict


@receiver(post_save, sender=SaleChannel)
def call_sku_and_seller_save_from_sc_save(sender, instance, *args, **kwargs):
    [seller.save() for seller in instance.sellers.all()]
    [sku.save() for sku in instance.skus.all()]


@receiver(post_delete, sender=SaleChannel)
def call_sku_and_seller_save_from_sc_delete(sender, instance, *args, **kwargs):
    [seller.save() for seller in instance.sellers.all()]
    [sku.save() for sku in instance.skus.all()]


class Seller(ChatbootModel):
    """Seller model."""

    # Filter data
    seller_id = models.CharField(_("Id of seller"), help_text=_("coud be a text instade a number"), max_length=500)
    name = models.CharField(_("Name of seller"), max_length=500)
    slug_name = models.SlugField(max_length=50, null=True, blank=True)
    hibrit_payment_options = models.BooleanField(_("Various forms of payment"), default=False, null=True)
    is_active = models.BooleanField(_("Status"), default=False)

    # Relationship filter
    store = models.ForeignKey("Store", verbose_name=_("Store"), on_delete=models.CASCADE)

    # Extra data
    description = models.CharField(_("Description of seller"), max_length=500)

    # raw data
    raw_json = models.JSONField(_("Raw data"))

    # Hack to db queries
    serializer_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        self.serializer_data = self.get_seller
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Sellers"
        default_related_name = 'sellers'

    @property
    def get_seller(self):
        seller_dict = {
            'id': self.seller_id,
            'name': self.name,
            'is_active': self.is_active,
            'descriptiom': self.description,
            'various_payment_iptions': self.hibrit_payment_options
        }
        return seller_dict


@receiver(post_save, sender=Seller)
def call_sku_seller_save_from_seller(sender, instance, *args, **kwargs):
    [sku_seller.save() for sku_seller in instance.sku_seller.all()]


class SkuSeller(ChatbootModel):

    # Filter data
    is_active = models.BooleanField(_("Status"))

    # Relationship filter
    sku = models.ForeignKey("products.Skus", verbose_name=_("Sku"), on_delete=models.CASCADE)
    seller = models.ForeignKey("Seller", verbose_name=_("Seller"), on_delete=models.CASCADE)

    # Raw data
    raw_json = models.JSONField(_("Raw data"))

    # Hack to db queries
    serializer_data = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.serializer_data = self.get_sku_seller
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Sku Seller'
        verbose_name_plural = 'Skus Sellers'
        default_related_name = 'sku_seller'

    @property
    def get_sku_seller(self):
        sku_seller_dict = {
            'sc': list(self.seller.sales_channel.values_list('external_id', flat=True)),
            'seller_id': self.seller.seller_id,
            'sku_id': self.sku.sku_id,
            'is_active': self.is_active
        }
        return sku_seller_dict
