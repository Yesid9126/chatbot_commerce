"""list of product with their skus."""

# Models
from chatbot_commerce.stores.models.stores import SkuSeller
from chatbot_commerce.products.models import (
    Skus, Product,
    Brand, Category, Department,
    Subcategory
)
from chatbot_commerce.stores.models import SaleChannel, Seller

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def update_or_create_product(store, product_id, vtex):
    product = vtex.product_unit(product_id=product_id)
    name = product.get('Name')
    if name:
        department = Department.objects.filter(external_id=product.get('DepartmentId'), store=store).last()
        category = Category.objects.filter(external_id=product.get('CategoryId'), department__store=store).last()
        sub_category = Subcategory.objects.filter(external_id=product.get('CategoryId'), category__department__store=store).last()
        if not category:
            if sub_category:
                category = sub_category.category
        try:
            product_instance, _ = Product.objects.update_or_create(
                store=store,
                external_id=product_id,
                defaults={
                    'name': name,
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
                }
            )
        except Exception as e:
            error = {
                'message': e,
                'product_id': product_id,
            }
            print(error)
            product_instance = None
    else:
        print(f'product not found try to get it from db: {product}')
        product_instance = Product.objects.filter(external_id=product_id).first()
    return product_instance


def update_or_create_sku(product_instance, product_id, sku, sku_id, vtex, store):

    # Quantity in warehouses
    total_quantity = 0
    if sku_id:
        sku_inventory = vtex.skus_inventory(sku_id=sku_id)
        sku_inventory = sku_inventory.get('balance')
        if sku_inventory:
            for quantity in sku_inventory:
                quantity_sku = quantity.get('totalQuantity')
                total_quantity += quantity_sku
    else:
        print(f'error in sku: {sku_id} line 164 utils/products.py')

    # Create or update sku
    try:
        # Get instance
        sku_instance, _ = Skus.objects.update_or_create(
            external_id=sku_id,
            product=product_instance,
            defaults={
                'name': sku.get('NameComplete'),
                'is_active': sku.get('IsActive'),
                'ref_id': sku.get('RefId'),
                'packaged_height': sku.get('Height'),
                'packaged_length': sku.get('Length'),
                'packaged_width': sku.get('Width'),
                'packaged_weight': sku.get('WeightKg'),
                'is_kit': sku.get('IsKit'),
                'comercial_condition_id': sku.get('CommercialConditionId'),
                'manufacter_code': sku.get('ManufacturerCode'),
                'reference_stock_id': sku.get('ReferenceStockKeepingUnitId'),
                'is_inventoried': sku.get('IsInventoried'),
                'is_transported': sku.get('IsTransported'),
                'total_quantity': total_quantity,
                'raw_json': sku
            }
        )
        # Get Sales channels of sku
        sc_ids = sku.get('SalesChannels')
        sc = SaleChannel.objects.filter(store=store, external_id__in=sc_ids)
        sku_instance.sales_channels.add(*sc)

        # Get Sellets of sku
        sellers_array = sku.get('SkuSellers')
        for seller_dict in sellers_array:
            seller_instance = Seller.objects.filter(store=store, seller_id=seller_dict.get('SellerId')).first()
            if seller_instance:
                SkuSeller.objects.update_or_create(
                    sku=sku_instance, seller=seller_instance,
                    defaults={
                        'is_active': seller_dict.get('IsActive'),
                        'raw_json': seller_dict
                    }

                )

    except Exception as e:
        error = {
            'message': e,
            'product_id': product_id,
            'sku_id': sku.get('Id'),
        }
        print(error)
        sku_instance = None
    return sku_instance


def create_products_vtex_store(store, limit=None):
    """Creation of product available in the store."""

    # Skus that will be created
    skus = []

    # Products that were successfuly updated
    products_created = []

    # Products that return a bad status code in the request
    products_not_found = []

    # Skus recently created
    skus_created = []

    # Skus that return a bad status code in the request
    skus_not_found = []

    # Set up request class
    vtex = VtexStores(store=store)

    # Get Sales channels in db
    sc = SaleChannel.objects.filter(store=store).values_list('external_id', flat=True)

    # Get skus to create
    for sc_id in sc:
        page = 1
        while 1:
            add = vtex.get_list_skus_by_storeid(store_id=sc_id, page=page)
            if add == {} or add == []:
                break
            print(add)
            skus += add
            page += 1
        if sc_id == 1:
            break
    db_sku_ids = Skus.objects.filter(product__store=store).values_list('external_id', flat=True).distinct('external_id')
    db_sku_ids = [int(sku_id) for sku_id in db_sku_ids if sku_id]
    skus = set(skus) - set(db_sku_ids)

    if skus:
        product_instance = None
        for sku_id in skus:
            print(f'sku_id: {sku_id}')

            # Get info sku
            for sc_id in sc:
                sku = vtex.get_sku_context(sku_id=sku_id, sc=sc_id)
                product_id = sku.get('ProductId')
                if product_id is not None:
                    break

            # Get product instance
            if product_id:

                # Reduce runtime for useless request
                if product_id in products_not_found:
                    product_instance = None

                # Getting a product instance if there's not one already
                elif not product_instance:
                    product_instance = update_or_create_product(store=store, product_id=product_id, vtex=vtex)

                    # Collection products with a bad request
                    if not product_instance:
                        products_not_found.append(product_id)

                    # Collection products with a good request
                    elif product_id not in products_created:
                        products_created.append(product_id)

                # Changing product instance
                elif product_id != product_instance.external_id:
                    product_instance = update_or_create_product(store=store, product_id=product_id, vtex=vtex)

                    # Collection products with a bad request
                    if not product_instance and product_id not in [*products_created, *products_not_found]:
                        products_not_found.append(product_id)

                    # Collection products with a good request
                    elif product_id not in [*products_created, *products_not_found]:
                        products_created.append(product_id)

                # Create sku
                sku_instance = update_or_create_sku(product_instance=product_instance, product_id=product_id, sku=sku, sku_id=sku_id, vtex=vtex, store=store)

                # Collection skus with a good request
                if sku_instance and int(sku_id) not in [*skus_created, *skus_not_found]:
                    skus_created.append(int(sku_id))

                # Collection skus with a bad request
                elif int(sku_id) not in [*skus_created, *skus_not_found]:
                    skus_not_found.append(int(sku_id))

                # Break creation if there's a limit
                if len(products_created) == limit:
                    break

    # Delete skus that don't have a product
    Skus.objects.filter(product=None).delete()

    print('Not found')
    print(f'products: {products_not_found}, skus: {skus_not_found}')

    # Return skus that will be used in other tasks
    return skus_created


def update_products_vtex_store(store):
    """Creation of product available in the store."""

    # Get list of skus in db
    skus = Skus.objects.filter(product__store=store).values_list('external_id', flat=True)

    # Products that were successfuly updated
    products_updated = []

    # Product that return a bad status code in the request
    products_not_found = []

    # Skus that return a bad status code in the request
    skus_not_found = []

    # Set up request class
    vtex = VtexStores(store=store)

    # Get Sales channels in db
    sc = SaleChannel.objects.filter(store=store).values_list('external_id', flat=True)

    if skus:
        product_instance = None
        for sku_id in skus:
            print(f'sku_id: {sku_id}')

            # Get info sku
            for sc_id in sc:
                sku = vtex.get_sku_context(sku_id=sku_id, sc=sc_id)
                product_id = sku.get('ProductId')
                if product_id is not None:
                    break

            # Get product instance
            if product_id:

                # Reduce runtime for useless request
                if product_id in products_not_found:
                    product_instance = None

                # Getting a product instance if there's not one already
                elif not product_instance:
                    product_instance = update_or_create_product(store=store, product_id=product_id, vtex=vtex)

                    # Collection products with a bad request
                    if not product_instance:
                        products_not_found.append(product_id)

                    # Collection products with a good request
                    elif product_id not in products_updated:
                        products_updated.append(product_id)

                # Changing product instance
                elif product_id != product_instance.external_id:
                    product_instance = update_or_create_product(store=store, product_id=product_id, vtex=vtex)

                    # Collection products with a bad request
                    if not product_instance and product_id not in [*products_updated, *products_not_found]:
                        products_not_found.append(product_id)

                    # Collection products with a good request
                    elif product_id not in [*products_updated, *products_not_found]:
                        products_updated.append(product_id)

                # Update sku
                sku_instance = update_or_create_sku(product_instance=product_instance, product_id=product_id, sku=sku, sku_id=sku_id, vtex=vtex, store=store)

                #  Collection skus with a bad request
                if sku_instance is None and int(sku_id) not in skus_not_found:
                    skus_not_found.append(int(sku_id))

    print('Not found')
    print(f'products: {products_not_found}, skus: {skus_not_found}')

    # Delete skus that don't have a product
    Skus.objects.filter(product=None).delete()
    return True
