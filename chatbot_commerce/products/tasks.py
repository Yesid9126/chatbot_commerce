"""Product tasks."""


# Celery
from celery.decorators import periodic_task
from celery.schedules import crontab


# Utils
from chatbot_commerce.utils.Product import get_Product_vtex_store
from chatbot_commerce.utils.departments_categories import get_departments


@periodic_task(name='departments_categories', run_every=crontab(day_of_week='*', hour=1, minute=30))
def departments_categories():
    """Create all Product and departments."""
    get_departments()
    get_Product_vtex_store()
    return True
