"""Product tasks."""


# Celery
from chatbot_commerce.products.models.products import Product
from celery.task import task


# Utils
from chatbot_commerce.utils.departments_categories import get_departments
from chatbot_commerce.utils.products import get_products_vtex_store
from chatbot_commerce.utils.departments_categories import get_brands
from chatbot_commerce.utils.celery.tasks import create_attributes, create_images, create_price

# Models
from chatbot_commerce.stores.models.stores import Store


@task(name='principal_periodic_task')
def principal_periodic_task(*args, **kwargs):
    """Create all Product and departments."""
    store = Store.objects.filter(name=kwargs['store']).first()
    get_brands(store)
    get_departments(store)
    skus = get_products_vtex_store(store=store)
    create_price.s(store=store.name, skus=skus).apply_async()
    create_attributes.s(store=store.name, skus=skus).apply_async()
    create_images.s(store=store.name, skus=skus).apply_async()
    print('new')
    return True


@task(name='store_begining')
def store_begining(store, *args, **kwargs):
    store = Store.objects.filter(name=store).first()
    get_brands(store)
    get_departments(store)
    skus = get_products_vtex_store(store=store, limit=10)
    create_price.s(store=store.name, skus=skus).apply_async()
    create_attributes.s(store=store.name, skus=skus).apply_async()
    create_images.s(store=store.name, skus=skus).apply_async()
    return True


@task(name='update_periodic_task')
def update_periodic_task(*args, **kwargs):
    """Create all Product and departments."""
    store = Store.objects.filter(name=kwargs['store']).first()
    get_brands(store)
    get_departments(store)
    products_skus = Product.objects.filter(store=store).order_by().values_list('external_id', flat=True).distinct()
    get_products_vtex_store(store=store, products_skus=products_skus)
    create_price.s(store=store.name).apply_async()
    create_attributes.s(store=store.name).apply_async()
    create_images.s(store=store.name).apply_async()
    print('new')
    return True
