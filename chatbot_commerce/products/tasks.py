"""Product tasks."""


# Celery
from celery.decorators import periodic_task
from celery.schedules import crontab


# Utils
from chatbot_commerce.utils.departments_categories import get_departments
from chatbot_commerce.utils.products import get_products_vtex_store

# Models
from chatbot_commerce.stores.models.stores import Store


@periodic_task(name='departments_categories', run_every=crontab(day_of_week='*', hour=1, minute=30))
def departments_categories():
    """Create all Product and departments."""
    for store in Store.objects.all():
        get_departments(store)
        get_products_vtex_store(store)
    return True
