"""Product tasks."""


# Celery
from celery import Celery

# Cache
from django.core.cache import cache


# Utils
from chatbot_commerce.utils.tasks import create_products_store, get_departments, get_brands, get_sc_sellers
import gc

# Models
from chatbot_commerce.stores.models import Store, TypeStore
from django.db import connections, transaction
from django_celery_beat.models import PeriodicTask, CrontabSchedule

app = Celery()
app.autodiscover_tasks()
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    STORE_TYPE = ('VTEX', 'SHOPIFY',)
    for store_type in STORE_TYPE:
        TypeStore.objects.get_or_create(name=store_type)
    # Calls clear_cache at 23:55.
    every_23_55, _ = CrontabSchedule.objects.get_or_create(day_of_week='*', hour=23, minute=55, timezone="America/Bogota")
    task_instance, _ = PeriodicTask.objects.get_or_create(name='limpiador', task='clear_cache', defaults=dict(crontab=every_23_55))


@app.task(name='clear_cache')
def clear_cache(*args, **kwargs):
    print('funcion 2')
    # This works as advertised on the memcached cache:
    cache.clear()
    # This manually purges the SQLite cache:
    cursor = connections['cache_database'].cursor()
    cursor.execute('DELETE FROM cache_table')
    transaction.commit_unless_managed(using='cache_database')
    gc.collect()
    return True


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
