# """Product tasks."""

# # Django
# from django.conf import settings

# # Django Rest Framework
# from rest_framework import status

# # Celery
# from config import celery_app
# from celery.decorators import task, periodic_task
# from celery.utils.log import get_task_logger
# from celery.schedules import crontab

# # Utils
# from chatbot_commerce.utils.sku_list import get_sku_vtex_store


# @task()
# def store_sku_list():
#     """List of all sku's"""
#     import ipdb ; ipdb.set_trace()
#     result = {}
#     response = get_sku_vtex_store()
#     result.append(response)
#     return result(status=status.HTTP_200_OK)