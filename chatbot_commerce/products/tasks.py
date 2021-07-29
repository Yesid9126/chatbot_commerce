"""Product tasks."""

# Django Rest Framework
from rest_framework import status

# Celery
from celery.decorators import task

# Utils
from chatbot_commerce.utils.products import get_products_vtex_store


@task(expires=259200, soft_time_limit=259200, time_limit=259200)
def store_products():
    """Create all products."""
    result = []
    response = get_products_vtex_store()
    result.append(response)
    response = status.HTTP_200_OK
    return response
