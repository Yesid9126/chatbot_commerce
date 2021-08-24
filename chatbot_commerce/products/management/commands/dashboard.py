from django.core.management.base import BaseCommand
from chatbot_commerce.utils.departments_categories import get_departments, get_brands
from chatbot_commerce.utils.products import get_products_vtex_store

# Models
from chatbot_commerce.stores.models.stores import Store


class Command(BaseCommand):

    def handle(self, *args, **options):
        for store in Store.objects.all():
            get_brands(store)
            print('Finish brands')
            get_departments(store)
            print('Finish Categories')
            get_products_vtex_store(store)
            print('Finish products')
