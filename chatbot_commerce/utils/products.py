"""list of product with their skus."""

# Models
from chatbot_commerce.products.models import (
    Skus, Product,
    Brand, Category, Department,
    Subcategory
)
from chatbot_commerce.stores.models import SaleChannel

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_products_vtex_store(store, limit=None, products_skus=[]):
    """Creation of product available in the store."""
    products_created = []
    skus_created = []

    vtex = VtexStores(store=store)
    if not products_skus:
        skus = []
        page = 1
        while 1:
            skus_ids = vtex.total_skus(page=page)
            if skus_ids == [] or page in [limit]:
                if limit is None:
                    store.last_page = page - 1
                print(f'Break in page: {page - 1}')
                break
            skus += skus_ids
            page += 1
        db_sku_ids = Skus.objects.filter(product__store__pk=store.pk).values_list('sku_id', flat=True).distinct('sku_id')
        db_sku_ids = [int(sku_id) for sku_id in db_sku_ids if sku_id.isnumeric()]
        skus = [sku_id for sku_id in skus if sku_id not in db_sku_ids]
        if skus:
            for sku_unit in skus:
                print(f'sku_id: {sku_unit}')
                sku = sku_unit
                product_id = vtex.unit_sku(sku=sku)
                product_id = product_id.get('ProductId')
                if product_id not in products_skus and type(product_id) is int:
                    products_skus.append(product_id)
                if len(products_skus) == limit:
                    break

    if products_skus:
        for product in products_skus:
            print(f'product_id: {product}')
            sub_category = None
            product = vtex.product_unit(product_id=product)
            department = Department.objects.filter(external_id=product.get('DepartmentId'), store=store).last()
            category = Category.objects.filter(external_id=product.get('CategoryId'), department__store=store).last()
            if not category:
                sub_category = Subcategory.objects.filter(external_id=product.get('CategoryId'), category__department__store=store).last()
                if not sub_category:
                    category = None
                else:
                    category = sub_category.category
            try:
                product_instance, _ = Product.objects.update_or_create(
                    store=store,
                    external_id=product.get('Id'),
                    defaults={
                        'name': product.get('Name'),
                        'department': department,
                        'sub_category': sub_category,
                        'category': category,
                        'brand': Brand.objects.filter(external_id=product.get('BrandId')).last(),
                        'link_id': product.get('LinkId'),
                        'reference_id': product.get('RefId'),
                        'is_visible': product.get('IsVisible'),
                        'description': product.get('Description'),
                        'description_short': product.get('DescriptionShort'),
                        'keywords': product.get('KeyWords'),
                        'title': product.get('Title'),
                        'is_active': product.get('IsActive'),
                        'meta_tag_description': product.get('MetaTagDescription'),
                        'show_without_stock': product.get('ShowWithoutStock'),
                        'raw_json': product,
                    })
                products_created.append(product_instance.pk)
            except Exception as e:
                error = {
                    'message': e,
                    'product_id': product.get('Id'),
                }
                print(error)

        # Create skus for product
        products_skus = Product.objects.filter(store__pk=store.pk, external_id__in=products_skus).order_by()
        for product in products_skus:
            product_id = product.external_id
            print(f'product object: {product}')
            skus_product = vtex.product_skus(product_id=product_id)
            for skus in skus_product:
                total_quantity = 0
                sku_id = skus.get('Id')
                if sku_id:
                    skus_inventory = vtex.skus_inventory(sku_id=sku_id)
                    sku_inventory = skus_inventory.get('balance')
                    for quantity in sku_inventory:
                        quantity_sku = quantity.get('totalQuantity')
                        total_quantity += quantity_sku
                else:
                    print(f'error in sku: {skus} 98 utils/products.py')
                try:
                    sku_instance, _ = Skus.objects.update_or_create(
                        sku_id=skus.get('Id'),
                        product=product,
                        defaults={
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
                            'total_quantity': total_quantity,
                            'sku_json': skus
                        }
                    )
                    skus_created.append(int(sku_instance.sku_id))
                except Exception as e:
                    error = {
                        'message': e,
                        'product_id': product_id,
                        'sku_id': skus.get('Id'),
                    }
                    print(error)
    Skus.objects.filter(product=None).delete()

    sales_channel = vtex.get_sales_channel()
    for channel in sales_channel:
        channel_id = channel.get('Id')
        if channel_id:
            list_skus_ids = vtex.get_list_skus_by_storeid(store_id=channel_id)
            print(f'store_id: {channel_id}')
            if type(list_skus_ids) is list:
                objs = Skus.objects.filter(product__store__pk=store.pk, sku_id__in=list_skus_ids).order_by()
            else:
                print(f'array {list_skus_ids} vacio for channel {channel_id}')
                objs = []
            instance_sale_channel, _ = SaleChannel.objects.update_or_create(
                store=store, external_id=channel_id,
                defaults={
                    'name': channel.get('Name'),
                    'is_active': channel.get('IsActive'),
                    'raw_json': channel | {'endpoint_sku_ids': list_skus_ids}
                }
            )
            instance_sale_channel.skus.add(*objs)
        else:
            print(f'channel: {channel}, sales_channel: {sales_channel}')

    return skus_created
