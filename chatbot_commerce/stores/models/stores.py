"""Stores model."""

# Raw
from slugify import slugify

# Django
from django.db import models

# Celery
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# utilities
from chatbot_commerce.utils.models import ChatbootModel
from django.utils.translation import gettext as _
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import requests


class Store(ChatbootModel):
    """Stores model."""

    name = models.CharField(
        max_length=255
    )
    slug_name = models.SlugField(max_length=50, unique=True, null=True, blank=True)

    url_enviroment = models.CharField(
        max_length=500, blank=True, null=True
    )

    api_key = models.CharField(
        max_length=500
    )

    api_token = models.CharField(
        max_length=500
    )

    sync_status = models.BooleanField(_("Task begun Finish"), default=False)

    status = models.BooleanField(_("Valid connection"), default=False)

    store_type = models.CharField(_("Type of store"), max_length=500)

    last_page = models.BigIntegerField(_("Last page get of skus"), default=0, blank=True, null=True)

    apply_filters = models.BooleanField(_("Apply filters"), default=True)

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
        store_begining.s(store=instance.name).apply_async(countdown=5)
    if instance.sync_status is True:
        every_100_years, _ = IntervalSchedule.objects.get_or_create(every=365*100, period=IntervalSchedule.DAYS)
        task_instance, _ = PeriodicTask.objects.get_or_create(name=f'all objects {instance.name}', task='departments_categories', defaults=dict(interval=every_100_years, kwargs='{"store": "%s"}' % (instance.name)))
    if instance.status is False or instance.sync_status is False:
        PeriodicTask.objects.filter(name=f'all objects {instance.name}', task='departments_categories').delete()


@receiver(post_delete, sender=Store)
def delete_task(sender, instance, *args, **kwargs):
    PeriodicTask.objects.filter(name=f'all objects {instance.name}', task='departments_categories').delete()
