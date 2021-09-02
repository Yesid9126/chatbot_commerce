"""Product tasks."""


# Celery
from celery.decorators import periodic_task
from celery.task import task
from celery.schedules import crontab


# Utils
from chatbot_commerce.utils.departments_categories import get_departments
from chatbot_commerce.utils.products import get_products_vtex_store
from chatbot_commerce.utils.departments_categories import get_brands

# Models
from chatbot_commerce.stores.models.stores import Store


@periodic_task(name='departments_categories', run_every=crontab(day_of_week='*', hour=1, minute=30))
def departments_categories(*args, **kwargs):
    """Create all Product and departments."""
    store = Store.objects.filter(name=kwargs['store']).first()
    get_brands(store)
    get_departments(store)
    get_products_vtex_store(store, limit=None)
    return True


@task(name='store_begining')
def store_begining(store, *args, **kwargs):
    store = Store.objects.filter(name=store).first()
    get_brands(store)
    get_departments(store)
    get_products_vtex_store(store, limit=10)
    return True
