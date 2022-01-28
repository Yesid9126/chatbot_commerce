"""Product tasks."""


# Celery
from config import celery_app
from celery import Celery
from django_celery_beat.models import PeriodicTask, IntervalSchedule
# from celery.schedules import crontab

# Django
from django.db.models import Q

# Django Utils
from chatbot_commerce.utils.tasks import create_products_store, get_departments, get_brands, get_sc_sellers
from django.utils import timezone

# Utils
# from pathlib import Path
import gc
import sys
import time

# Models
from chatbot_commerce.stores.models import Store, TypeStore, Price, FixedPrice, DateRange, AttributeType, Attribute, Sku, Image

# interval_instance, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.SECONDS)
# task_instance, _ = PeriodicTask.objects.get_or_create(name='Update models serializer', task='continue_update_models')

# Calls clear_cache at 23:55.
# every_23_55, _ = CrontabSchedule.objects.get_or_create(day_of_week='*', hour=23, minute=55, timezone="America/Bogota")
# task_instance, _ = PeriodicTask.objects.get_or_create(name='limpiador', task='clear_cache', defaults=dict(crontab=every_23_55))

STORE_TYPE = ('VTEX', 'SHOPIFY',)
for store_type in STORE_TYPE:
    TypeStore.objects.get_or_create(name=store_type)

app = Celery()
# update_serializer_data
# set_fixed_prices


@celery_app.task(name='update_serializer_data')
def update_serializer_data():
    """Manage price of warehouse products"""

    from_date_time_date_ranges =\
        from_date_time_fixed_prices =\
        from_date_time_prices =\
        from_date_time_attribute_type =\
        from_date_time_attributes =\
        from_date_time_images = timezone.now() - timezone.timedelta(days=2)
    ids_list = queryset = skus_ids_list = attributes_ids_list = set()
    update_date_ranges = DateRange.objects.filter(modified__gte=from_date_time_date_ranges, fixed_price__price__sku__is_active=True).exists()
    if update_date_ranges:
        ids_list = set(DateRange.objects.filter(modified__gte=from_date_time_date_ranges, fixed_price__price__sku__is_active=True).values_list('fixed_price__id', flat=True))
        queryset = set(FixedPrice.objects.filter(pk__in=ids_list))
        ids_list.clear()
        [fixed.set_date_range for fixed in queryset]
        queryset.clear()

    update_fixed_prices = FixedPrice.objects.filter(modified__gte=from_date_time_fixed_prices, price__sku__is_active=True).exists()
    if update_fixed_prices:
        ids_list = set(FixedPrice.objects.filter(modified__gte=from_date_time_fixed_prices, price__sku__is_active=True).values_list('price__pk', flat=True))
        queryset = set(Price.objects.filter(pk__in=ids_list))
        ids_list.clear()
        [price.set_fixed_prices for price in queryset]
        queryset.clear()

    update_prices = Price.objects.filter(modified__gte=from_date_time_prices, sku__is_active=True).exists()
    if update_prices:
        skus_ids_list = set(Price.objects.filter(modified__gte=from_date_time_prices, sku__is_active=True).values_list('sku__pk', flat=True))

    update_attribute_type = AttributeType.objects.filter(modified__gte=from_date_time_attribute_type).exists()
    if update_attribute_type:
        attribute_type_ids_list = set(AttributeType.objects.filter(modified__gte=from_date_time_attribute_type).values_list('pk', flat=True))
        attributes_ids_list = set(Attribute.objects.filter(attribute_type__in=attribute_type_ids_list).values_list('pk', flat=True))
        skus_ids_list = set(Sku.objects.filter(~Q(pk__in=skus_ids_list), is_active=True, attributes__in=attributes_ids_list).values_list('pk', flat=True)) | skus_ids_list
        attributes_ids_list.clear()

    update_attributes = Attribute.objects.filter(modified__gte=from_date_time_attributes).exists()
    if update_attributes:
        attributes_ids_list = set(Attribute.objects.filter(modified__gte=from_date_time_attributes).values_list('pk', flat=True)) - attributes_ids_list
        skus_ids_list = set(Sku.objects.filter(~Q(pk__in=skus_ids_list), is_active=True, attributes__in=attributes_ids_list).values_list('pk', flat=True)) | skus_ids_list
        attributes_ids_list.clear()

    update_images = Image.objects.filter(modified__gte=from_date_time_images).exists()
    if update_images:
        image_ids_list = set(Image.objects.filter(modified__gte=from_date_time_images).values_list('pk', flat=True))
        skus_ids_list = set(Sku.objects.filter(~Q(pk__in=skus_ids_list), is_active=True, images__in=image_ids_list).values_list('pk', flat=True)) | skus_ids_list

    if skus_ids_list:
        queryset = set(Sku.objects.filter(pk__in=skus_ids_list))
        skus_ids_list.clear()
        [sku.update_serializer_data for sku in queryset]
        queryset.clear()


try:
    container_name = sys.argv[-3]
except Exception:
    container_name = ''
if container_name == 'worker':
    # update_serializer_data.s().apply_async(countdown=1)
    interval_instance, _ = IntervalSchedule.objects.get_or_create(every=6, period=IntervalSchedule.HOURS)
    task_instance, _ = PeriodicTask.objects.get_or_create(name='Update models serializer', task='update_serializer_data', interval=interval_instance)
print("container_name:", container_name)


@celery_app.task(name='store_begining')
def store_begining(store, *args, **kwargs):
    """Create Products, Skus, Categories and Brands."""

    # Validations
    try:
        store = Store.objects.select_related('store_type').get(pk=store)
    except Exception as message:
        return f'error: store no match, message_error: {message}'
    if store.sync_status:
        return 'sync_status already runed'
    store.sync_status = True
    store.save()

    # brands, categories, products and skus
    get_sc_sellers(store=store, task='create')
    gc.collect()
    get_brands(store)
    gc.collect()
    get_departments(store)
    gc.collect()
    create_products_store(store=store, limit=True)
    gc.collect()

    return True


@celery_app.task(name='principal_periodic_task')
def principal_periodic_task(*args, **kwargs):
    """Update Products, Skus, Categories and Brands."""

    # Validations
    try:
        store = Store.objects.get(pk=kwargs['store'])
    except Exception as message:
        return f'error: store no match, message_error: {message}'
    if store.creating_updating_elements_status:
        if not store.sync_status:
            return 'sync_status: Failed'
        return 'task already running'
    store.creating_updating_elements_status = True
    store.save()
    try:

        # brands, categories, products and skus
        get_sc_sellers(store=store)
        gc.collect()
        get_brands(store)
        gc.collect()
        get_departments(store)
        gc.collect()
        create_products_store(store=store)
        gc.collect()

    except Exception as message:
        store.creating_updating_elements_status = False
        store.save()
        raise message

    store.creating_updating_elements_status = False
    store.save()
    return True
