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
                oelo, created = Skus.objects.update_or_create(
                    sku_id=skus.get('Id'),
                    defaults={
                        'product_id': skus.get('ProductId'),
                        'sku_name': skus.get('Name'),
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


# def get_skus_vtex_stores(request, **kwargs):
#     """Get skus for product."""
#     vtex = VtexStores()
#     products = ProductsApiVtex.objects,all()
#     for sku in products:
#         import ipdb ; ipdb.set_trace()
#         product_id = products.get('product_id')
#         import ipdb ; ipdb.set_trace()
    # skus = vtex.total_skus()
    # if skus:
    #     for sku_unit in skus:
    #         sku = sku_unit
    #         sku = vtex.unit_sku(sku=sku)
    #         product = ProductsApiVtex.objects.filter(product_id=sku.get('ProductId')).get()
    #         try:
    #             products_sku, created = Skus.objects.update_or_create(
    #                 sku_id=sku.get('Id'),
    #                 defaults={
    #                     'product_id': sku.get('ProductId'),
    #                     'sku_name': sku.get('Name'),
    #                     'is_active': sku.get('IsActive'),
    #                     'activate_if_possible': sku.get('ActivateIfPossible'),
    #                     'refID': sku.get('RefId'),
    #                     'packaged_height': sku.get('PackagedHeight'),
    #                     'packaged_length': sku.get('PackagedLength'),
    #                     'packaged_width': sku.get('PackagedWidth'),
    #                     'packaged_weight': sku.get('PackagedWeightKg'),
    #                     'is_kit': sku.get('IsKit'),
    #                     'comercial_condition_id': sku.get('CommercialConditionId'),
    #                     'unit_multiplier': sku.get('UnitMultiplier'),
    #                     'kit_items_sell_apart': sku.get('KitItensSellApart'),
    #                     'products': product,
    #                     'sku_json': sku
    #                 }
    #             )
    #         except Exception as e:
    #             # if not created:
    #                 print('Error al crear')
    #             #     # product.status = Product.RETRIEVED_FROM_SHOPIFY
    #             #     # product.save(update_fields=['status', 'modified'])
    #             # else:
    #             #     # TODO: Product with multiples variants
    #             #     pass
    # # Delete products not in store
    # all_products = ProductsApiVtex.objects.all()
    # non_existence_ids = all_products.exclude(product_id__in=products_ids)
    # non_existence_ids.delete()
    # return products_ids
