"""Store sku list"""

# Django Rest Framework
from rest_framework import status

# Models
from chatbot_commerce.products.models import Skus

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_sku_vtex_store():
    """Get all sku's available in shop."""
    vtex = VtexStores()
    skus = vtex.total_skus()
    skus_ids = []
    if skus:
        for sku in skus:
            id_product = product.get('id')
            shopify_ids.append(str(id_product))
            variants = product.get('variants')
            # Check single or multiple variants
            for variant in variants:
                if id_product == variant.get('product_id'):
                    # Create product
                    try:
                        product, created = Product.objects.update_or_create(
                            id_shopify=id_product,
                            defaults={
                                'sku': variant.get('sku'),
                                'name': product.get('title'),
                                'stock': variant.get('inventory_quantity'),
                                'product_data': product,
                            })
                    except Exception as e:
                        logger.error(f'Cant retrieve product from shopify due: {e}')
                    if not created:
                        product.status = Product.RETRIEVED_FROM_SHOPIFY
                        product.save(update_fields=['status', 'modified'])
                else:
                    # TODO: Product with multiples variants
                    pass
        # Delete products not in store
        all_products = Product.objects.all()
        non_existence_ids = all_products.exclude(id_shopify__in=shopify_ids)
        non_existence_ids.delete()
        return f'{len(shopify_ids)} products retrieved from shopify'
    else:
        logger.error(f'Error in import products by shopify {stock}')
