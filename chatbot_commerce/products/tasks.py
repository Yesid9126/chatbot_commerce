"""Product tasks."""


# Celery
from celery import Celery


# Utils
from chatbot_commerce.utils.departments_categories import get_departments, get_brands, get_sc_sellers
from chatbot_commerce.utils.products import create_products_vtex_store

# Models
from chatbot_commerce.stores.models.stores import Store

app = Celery()


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

    # brands, categories, products and skus
    get_sc_sellers(store=store, task='create')
    get_brands(store)
    get_departments(store)
    create_products_vtex_store(store=store, limit=True)

    store.sync_status = True
    store.save()
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
        get_brands(store)
        get_departments(store)
        create_products_vtex_store(store=store)

    except Exception as message:
        print(f'error: {message}')

    store.creating_updating_elements_status = False
    store.save()
    print('new')
    return True
