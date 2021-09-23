"""Product tasks."""


# Celery
from celery import Celery


# Utils
from chatbot_commerce.utils.departments_categories import get_departments, get_brands, get_sc_sellers
from chatbot_commerce.utils.products import create_products_vtex_store, update_products_vtex_store
from chatbot_commerce.utils.celery.tasks import create_attributes, create_images, create_price
import threading

# Models
from chatbot_commerce.stores.models.stores import Store

app = Celery()


@app.task(name='principal_periodic_task')
def principal_periodic_task(*args, **kwargs):
    """Starting Products, Skus, Categories and Brands."""

    # Validations
    try:
        store = Store.objects.get(pk=kwargs['store'])
    except Exception as message:
        return f'error: store no match, message_error: {message}'
    if store.creating_elements_status:
        if not store.sync_status:
            return 'sync_status: False'
        return 'task already running'
    store.creating_elements_status = True
    store.save()
    try:
        store_pk = store.pk

        # brands, categories products and skus
        get_sc_sellers(store=store, task='create')
        get_brands(store)
        get_departments(store)

        skus = create_products_vtex_store(store=store)

        # skus extra components
        create_price.s(store_pk=store_pk, skus=skus).apply_async()
        create_images(store=store, skus=skus)
        create_attributes(store=store, skus=skus)

    except Exception as message:
        print(f'error: {message}')

    store.creating_elements_status = False
    store.save()
    print('new')
    return True


@app.task(name='store_begining')
def store_begining(store, *args, **kwargs):
    """Create Products, Skus, Categories and Brands."""

    # Validations
    try:
        store = Store.objects.get(pk=store)
    except Exception as message:
        return f'error: store no match, message_error: {message}'
    if store.sync_status:
        return 'sync_status already runed'
    store_pk = store.pk

    # brands, categories, products and skus
    get_sc_sellers(store=store, task='create')
    get_brands(store)
    get_departments(store)
    skus = create_products_vtex_store(store=store, limit=10)

    # skus extra components
    create_price.s(store_pk=store_pk, skus=skus).apply_async()
    create_images(store=store, skus=skus)
    create_attributes(store=store, skus=skus)

    store.sync_status = True
    store.save()
    return True


@app.task(name='update_periodic_task')
def update_periodic_task(*args, **kwargs):
    """Update Products, Skus, Categories and Brands."""

    # Validations
    try:
        store = Store.objects.get(pk=kwargs['store'])
    except Exception as message:
        return f'error: store no match, message_error: {message}'
    if store.updating_elements_status:
        if not store.sync_status:
            return 'sync_status: False'
        return 'task already running'
    store.updating_elements_status = True
    store.save()
    try:
        store_pk = store.pk

        # brands, categories, products and skus
        get_sc_sellers(store=store)
        get_brands(store)
        get_departments(store)
        update_products_vtex_store(store=store)

        # skus extra components
        create_price.s(store_pk=store_pk).apply_async()
        create_images(store=store)
        create_attributes(store=store)

    except Exception as message:
        print(f'error: {message}')

    store.updating_elements_status = False
    store.save()
    print('new')
    return True
