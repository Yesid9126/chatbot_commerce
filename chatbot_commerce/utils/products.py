"""list of products with their skus."""

# Models
from chatbot_commerce.products.models import Skus, ProductsApiVtex

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_sku_vtex_store():
    """Creation of products available in the store."""
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
    for product in products_ids:
        products = vtex.product_unit(product_id=product)
        products, created = ProductsApiVtex.objects.update_or_create(
            product_id=products.get('Id'),
            defaults={
                'name': products.get('Name'),
                'link_id': products.get('LinkId'),
                'reference_id': products.get('RefId'),
                'is_visible': products.get('IsVisible'),
                'description': products.get('Description'),
                'description_short': products.get('DescriptionShort'),
                'keywords': products.get('KeyWords'),
                'title': products.get('Title'),
                'is_active': products.get('IsActive'),
                'meta_tag_description': products.get('MetaTagDescription'),
                'show_without_stock': products.get('ShowWithoutStock'),
                'product_data': products,
            })
        skus = vtex.products_skus(product_id=product)
        for products_skus in skus:
            if product == products_skus.get('ProductId'):
                products = ProductsApiVtex.objects.filter(product_id=product).get()
                skus, created = Skus.objects.update_or_create(
                    sku_id=products_skus.get('Id'),
                    products=products,
                    defaults={
                        'product_id': product,
                        'is_active': products_skus.get('IsActive'),
                        'specification': products_skus.get('Name'),
                        'refID': products_skus.get('RefId'),
                        'is_kit': products_skus.get('IsKit'),
                        'comercial_condition_id': products_skus.get('CommercialConditionId'),
                        'sku_json': products_skus
                    }
                )
        # departments = vtex
