"""list of products with their skus."""

# Models
from chatbot_commerce.products.models import Skus, ProductsApiVtex

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_products_vtex_store():
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
        try:
            products, created = ProductsApiVtex.objects.update_or_create(
                product_id=products.get('Id'),
                defaults={
                    'name': products.get('Name'),
                    'department_id': products.get('DepartmentId'),
                    'category_id': products.get('CategoryId'),
                    'brand_id': products.get('BrandId'),
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
        except Exception as e:
            error = e
    # Create skus for product
    for product in products_ids:
        skus_product = vtex.products_skus(product_id=product)
        for skus in skus_product:
            products = ProductsApiVtex.objects.filter(product_id=product).get()
            try:
                product_skus, created = Skus.objects.update_or_create(
                    sku_id=skus.get('Id'),
                    defaults={
                        'product_id': skus.get('ProductId'),
                        'sku_name': skus.get('Name').upper(),
                        'is_active': skus.get('IsActive'),
                        'ref_id': skus.get('RefId'),
                        'packaged_height': skus.get('Height'),
                        'packaged_length': skus.get('Length'),
                        'packaged_width': skus.get('Width'),
                        'packaged_weight': skus.get('WeightKg'),
                        'is_kit': skus.get('IsKit'),
                        'comercial_condition_id': skus.get('CommercialConditionId'),
                        'manufacter_code': skus.get('ManufacturerCode'),
                        'reference_stock_id': skus.get('ReferenceStockKeepingUnitId'),
                        'is_inventoried': skus.get('IsInventoried'),
                        'is_transported': skus.get('IsTransported'),
                        'products': products,
                        'sku_json': skus
                    }
                )
            except Exception as e:
                error = e
                print(error)
    # Delete products not in store
    all_products = ProductsApiVtex.objects.all()
    non_existence_ids = all_products.exclude(product_id__in=products_ids)
    non_existence_ids.delete()
    return f'{len(products_ids)} products retrieved from vtex'
