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

app = Celery()


@app.task(name='principal_periodic_task')
def principal_periodic_task(*args, **kwargs):
    """Starting Products, Skus, Categories and Brands."""

    # Validations
    store = Store.objects.filter(name=kwargs['store']).first()
    if store.creating_elements_status:
        if not store.sync_status:
            return 'sync_status: False'
        return 'task already running'
    store.creating_elements_status = True
    store.save()

    # brands, categories products and skus
    get_brands(store)
    get_departments(store)
    skus = get_products_vtex_store(store=store)

    # skus extra components
    create_price.s(store=store.name, skus=skus).apply_async()
    create_images.s(store=store.name, skus=skus).apply_async()
    create_attributes(store=store.name, skus=skus)

    store.creating_elements_status = False
    store.save()
    print('new')
    return True


@app.task(name='store_begining')
def store_begining(store, *args, **kwargs):
    """Create Products, Skus, Categories and Brands."""

    # Validations
    store = Store.objects.filter(name=store).first()
    if store.sync_status:
        return 'sync_status already runed'

    # brands, categories, products and skus
    get_brands(store)
    get_departments(store)
    skus = get_products_vtex_store(store=store, limit=10)

    # skus extra components
    create_price.s(store=store.name, skus=skus).apply_async()
    create_images.s(store=store.name, skus=skus).apply_async()
    create_attributes(store=store.name, skus=skus)

    store.sync_status = True
    store.save()
    return True


@app.task(name='update_periodic_task')
def update_periodic_task(*args, **kwargs):
    """Update Products, Skus, Categories and Brands."""

    # Validations
    store = Store.objects.filter(name=kwargs['store']).first()
    if store.updating_elements_status:
        if not store.sync_status:
            return 'sync_status: False'
        return 'task already running'
    store.updating_elements_status = True
    store.save()

    # brands, categories, products and skus
    get_brands(store)
    get_departments(store)
    products_skus = Product.objects.filter(store=store).order_by().values_list('external_id', flat=True).distinct()
    get_products_vtex_store(store=store, products_skus=products_skus)

    # skus extra components
    create_price.s(store=store.name).apply_async()
    create_images.s(store=store.name).apply_async()
    create_attributes(store=store.name)

    store.updating_elements_status = False
    store.save()
    print('new')
    return True
