"""Product tasks."""

# Django Rest Framework
from rest_framework import status

# Models
from chatbot_commerce.stores.models import StoresVtex

# Celery
from config import celery_app
from celery.decorators import task, periodic_task
from celery.utils.log import get_task_logger

# Utils
from chatbot_commerce.utils.products import get_sku_vtex_store
# from chatbot_commerce.utils.departments_categories import get_departments


@task(expires=259200, soft_time_limit=259200, time_limit=259200)
def store_products():
    """List of all products and sku's"""
    result = []
    for store in StoresVtex.objects.all():
        response = get_sku_vtex_store()
        result.append(response)
    response = status.HTTP_200_OK
    return response

# @task(expires=259200, soft_time_limit=259200, time_limit=259200)
# def store_departments():
#     """List of departments and categories for store"""
#     result = []
#     response = get_departments()
#     result.append(response)
#     return result(status=status.HTTP_200_OK)
