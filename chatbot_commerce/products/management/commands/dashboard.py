from django.core.management.base import BaseCommand
from chatbot_commerce.products.tasks import departments_categories
from chatbot_commerce.utils.departments_categories import get_brands
from chatbot_commerce.utils.products import get_products_vtex_store


class Command(BaseCommand):

    def handle(self, *args, **options):
        get_brands()
        print('Finish brands')
        departments_categories()
        print('Finish Categories')
        get_products_vtex_store()
        print('Finish products')
