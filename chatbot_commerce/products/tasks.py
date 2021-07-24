"""Product tasks."""

# Django
from django.conf import settings

# Django Rest Framework
from rest_framework import status
from rest_framework import response

# Celery
from config import celery_app
from celery.decorators import task, periodic_task
from celery.utils.log import get_task_logger
from celery.schedules import crontab

# Utils
from chatbot_commerce.utils.products import get_sku_vtex_store


@task(expires=259200, soft_time_limit=259200, time_limit=259200)
def store_sku_list():
    """List of all sku's"""
    result = []
    response = get_sku_vtex_store()
    result.append(response)
    return response(status=status.HTTP_200_OK)
