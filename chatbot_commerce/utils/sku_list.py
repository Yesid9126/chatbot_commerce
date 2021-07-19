"""Store sku list"""

# Django Rest Framework
from rest_framework import status

# Models
from chatbot_commerce.products.models import Skus, ProductsApiVtex

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_sku_vtex_store(request, **kwargs):
    """Get all sku's available in shop."""
    vtex = VtexStores()
    skus = vtex.total_skus()
    products_ids = []
    if skus:
        for sku_unit in skus:
            sku = sku_unit
            product_id = vtex.unit_sku(sku=sku)
            product_id = product_id.get('ProductId')
            if product_id not in products_ids:
                products_ids.append(product_id)
    # for products in products_ids:
    #     products = vtex.product_unit(product_id=products)
    #     if products:
    #         try:
    #             products, created = ProductsApiVtex.objects.update_or_create(
    #                     product_id=products.get('Id'),
    #                     defaults={
    #                         'product_id': product_id.get('ProductId'),
    #                         'is_active': product_id.get('IsActive'),
    #                         'specification': product_id.get('Name'),
    #                         'sku_json': product_id,
    #                     })
            
            # try:
            #     product_id, created = Skus.objects.update_or_create(
            #                 sku_id=product_id.get('Id'),
            #                 defaults={
            #                     'product_id': product_id.get('ProductId'),
            #                     'is_active': product_id.get('IsActive'),
            #                     'specification': product_id.get('Name'),
            #                     'sku_json': product_id,
            #                 })
            # except ConnectionError:
            #     continue
            
                
