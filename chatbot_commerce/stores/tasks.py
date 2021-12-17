"""Product tasks."""


# Celery
from celery import Celery
# from celery.schedules import crontab

# Cache
# from django.core.cache import cache


# Utils
from chatbot_commerce.utils.tasks import create_products_store, get_departments, get_brands, get_sc_sellers
# from pathlib import Path
import gc
import time
import os

# Models
from chatbot_commerce.stores.models import Store, TypeStore, UpdateModels, Product, Sku, Price
from django_celery_beat.models import PeriodicTask

# interval_instance, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.SECONDS)
# task_instance, _ = PeriodicTask.objects.get_or_create(name='Update models serializer', task='continue_update_models')

STORE_TYPE = ('VTEX', 'SHOPIFY',)
for store_type in STORE_TYPE:
    TypeStore.objects.get_or_create(name=store_type)

app = Celery()

app.autodiscover_tasks()

# Calls clear_cache at 23:55.
# every_23_55, _ = CrontabSchedule.objects.get_or_create(day_of_week='*', hour=23, minute=55, timezone="America/Bogota")
# task_instance, _ = PeriodicTask.objects.get_or_create(name='limpiador', task='clear_cache', defaults=dict(crontab=every_23_55))


# @app.task(name='clear_cache')
# def clear_cache(*args, **kwargs):
#     # This works as advertised on the memcached cache:
#     cache.clear()
#     # This manually purges the SQLite cache:
#     cursor = connections['cache_database'].cursor()
#     cursor.execute('DELETE FROM cache_table')
#     transaction.commit_unless_managed(using='cache_database')
#     gc.collect()
#     return True

@app.task(name='continue_update_models')
def continue_update_models(*args, **kwargs):
    while 1:
        if UpdateModels.objects.exclude(model_name='continue_update_models').exists():
            print('exists')
            array_skus_all_data = UpdateModels.objects.filter(model_name='Sku').values_list('all_data', flat=True)
            array_products_all_data = UpdateModels.objects.filter(model_name='Product').values_list('all_data', flat=True)
            array_prices_all_data = UpdateModels.objects.filter(model_name='Price').values_list('all_data', flat=True)
            if array_skus_all_data:
                for _, fn, pk in array_skus_all_data:
                    if fn == 'set_attributes':
                        UpdateModels.objects.filter(model_name='Sku', function_name='set_attributes', primary_key=pk).delete()
                        Sku.objects.filter(pk=pk).last().set_attributes
                    elif fn == 'set_images':
                        UpdateModels.objects.filter(model_name='Sku', function_name='set_images', primary_key=pk).delete()
                        Sku.objects.filter(pk=pk).last().set_images
                    elif fn == 'set_sellers':
                        UpdateModels.objects.filter(model_name='Sku', function_name='set_sellers', primary_key=pk).delete()
                        Sku.objects.filter(pk=pk).last().set_sellers
            if array_products_all_data:
                for _, fn, pk in array_products_all_data:
                    if fn == 'set_images':
                        UpdateModels.objects.filter(model_name='Product', function_name='set_images', primary_key=pk).delete()
                        Product.objects.filter(pk=pk).last().set_images
            if array_prices_all_data:
                for _, fn, pk in array_prices_all_data:
                    if fn == 'set_fixed_prices':
                        UpdateModels.objects.filter(model_name='Price', function_name='set_fixed_prices', primary_key=pk).delete()
                        Price.objects.filter(pk=pk).last().set_fixed_prices
        time.sleep(5)

continue_update_models.s().apply_async()

@app.task(name='store_begining')
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


@app.task(name='principal_periodic_task')
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
        print(f'error: {message}')

    store.creating_updating_elements_status = False
    store.save()
    return True
