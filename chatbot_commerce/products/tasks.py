"""Product tasks."""


# Celery
from chatbot_commerce.products.models.products import Product
from celery import Celery


# Utils
from chatbot_commerce.utils.departments_categories import get_departments
from chatbot_commerce.utils.products import get_products_vtex_store
from chatbot_commerce.utils.departments_categories import get_brands
from chatbot_commerce.utils.celery.tasks import create_attributes, create_images, create_price

# Models
from chatbot_commerce.stores.models.stores import Store
# from chatbot_commerce.products.models import Skus

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
        get_brands(store)
        get_departments(store)
        skus = get_products_vtex_store(store=store)

        # skus extra components
        create_price.s(store_pk=store_pk, skus=skus).apply_async()
        create_images.s(store_pk=store_pk, skus=skus).apply_async()
        create_attributes(store_pk=store_pk, skus=skus)
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
    get_brands(store)
    get_departments(store)
    skus = get_products_vtex_store(store=store, limit=10)

    # skus extra components
    create_price.s(store_pk=store_pk, skus=skus).apply_async()
    create_images.s(store_pk=store_pk, skus=skus).apply_async()
    create_attributes(store_pk=store_pk, skus=skus)

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
        get_brands(store)
        get_departments(store)
        products_skus = Product.objects.filter(store__pk=store.pk).order_by().values_list('external_id', flat=True).distinct('external_id')
        get_products_vtex_store(store=store, products_skus=products_skus)

        # skus extra components
        create_price.s(store_pk=store_pk).apply_async()
        create_images.s(store_pk=store_pk).apply_async()
        create_attributes(store_pk=store_pk)
    except Exception as message:
        print(f'error: {message}')

    store.updating_elements_status = False
    store.save()
    print('new')
    return True
