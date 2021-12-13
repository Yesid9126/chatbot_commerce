from rest_framework.decorators import api_view

from django.db import connection, reset_queries
from chatbot_commerce.stores.models import Product, Sku, Store
from rest_framework.response import Response
from django.db.models import Prefetch
import time
import functools

from chatbot_commerce.stores.serializers import ProductModelSerializer


def query_debugger(func):

    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function: {func.__name__}")
        print(f"Number of Queries: {end_queries - start_queries}")
        print(f"Finished in: {(end - start):.3f}s")

        return result

    return inner_func


@api_view()
@query_debugger
def product_list(request):
    store = Store.objects.get(name='pilatos21')
    skus = Sku.objects.filter(product__store=store)
    queryset = Product.objects\
        .select_related('department', 'category', 'sub_category', 'brand')\
        .prefetch_related(Prefetch('skus', queryset=skus))\
        .filter(store=store).distinct('pk').order_by('-pk')
    print(len(queryset))
    # products = []
    # for product in queryset:
    #     if product.sub_category:
    #         category_tree = {
    #             'name': product.sub_category.name,
    #             'category': {
    #                 'name': product.category.name,
    #                 'department': {
    #                     'name': product.department.name
    #                 }
    #             }
    #         }
    #     elif product.category:
    #         category_tree = {
    #             'name': product.category.name,
    #             'department': {
    #                 'name': product.department.name
    #             }
    #         }
    #     else:
    #         category_tree = {
    #             'name': product.department.name
    #         }
    #     response = {
    #         'id': product.external_id,
    #         'title': product.title,
    #         'is_visible': product.is_visible,
    #         'category_tree': category_tree,
    #         'is_active': product.is_active,
    #         'keywords': product.keywords,
    #         'description_short': product.description_short,
    #         'skus': product.skus.values_list('serializer_data', flat=True)
    #     }
    #     products.append(response)

    return Response(ProductModelSerializer(queryset, many=True).data)


@query_debugger
def queryset_products_serialzier(queryset):
    products = []
    for product in queryset:
        if product.sub_category:
            category_tree = {
                'name': product.sub_category.name,
                'category': {
                    'name': product.category.name,
                    'department': {
                        'name': product.department.name
                    }
                }
            }
        elif product.category:
            category_tree = {
                'name': product.category.name,
                'department': {
                    'name': product.department.name
                }
            }
        else:
            category_tree = {
                'name': product.department.name
            }
        if product.brand:
            brand = {
                'name': product.brand.name,
                'slug_name': product.brand.slug_name
            }
        response = {
            'id': product.external_id,
            'name': product.name,
            'keywords': product.keywords,
            'brand': brand,
            'category_tree': category_tree,
            'is_active': product.is_active,
            'description_short': product.description_short,
        }
        products.append(response)

    return products
