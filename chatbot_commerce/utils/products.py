"""list of product with their skus."""

# Models
import asgiref
from chatbot_commerce.stores.models.stores import SkuSeller
from chatbot_commerce.products.models import (
    Skus, Product,
    Brand, Category, Department,
    Subcategory
)
from chatbot_commerce.stores.models import SaleChannel, Seller

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores

# Utils
import asyncio

def update_or_create_product(store, product, product_id, vtex):
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


def update_or_create_sku(product_instance, product_id, sku, vtex, store):

    # Create or update sku
    try:
        # Get instance
        sku_instance, _ = Skus.objects.update_or_create(
            external_id=sku.get('Id'),
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
                'total_quantity': sku.get('total_quantity'),
                'raw_json': sku
            }
        )
        # Get Sales channels of sku
        sc_ids = sku.get('SalesChannels')
        sc = SaleChannel.objects.filter(store=store, external_id__in=sc_ids)
        sku_instance.sales_channels.add(*sc)

        # Get Sellers of sku
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

async def get_skus_and_products_dicts(sc, loop, vtex, store, db_sku_ids=[], skus=[]):
    print('inicio')
    # Skus that will be created
    if not skus:
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
        # Filter skus to create that there's npt in db
        skus = set(skus) - set(db_sku_ids)
    print('aaaaaa')
    # Get dicts skus
    asynciofunctions_skus = [loop.run_in_executor(None, vtex.get_sku_context, sku_id, sc_id) for sc_id in sc if sc_id in ['1', 1] for sku_id in skus]
    print('preparty aaaaa')
    skus_dicts = [await asynciofunction_sku for asynciofunction_sku in asynciofunctions_skus]
    print('final aaaaaa')
    # Get dicts products
    print('bbbbb')
    asynciofunctions_products = [loop.run_in_executor(None, vtex.product_unit, sku_dict.get('ProductId')) for sku_dict in skus_dicts if sku_dict.get('ProductId')]
    print('preparty bbbbb')
    products_dicts = [await asynciofunction_product for asynciofunction_product in asynciofunctions_products]
    print('final bbbbb')
    # Returning values
    return skus_dicts, products_dicts
        

def create_products_vtex_store(store, limit=None):
    """Creation of product available in the store."""

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
    sc = list(SaleChannel.objects.filter(store=store).values_list('external_id', flat=True))

    # Skus ids in db
    db_sku_ids = list(Skus.objects.filter(product__store=store).values_list('external_id', flat=True).distinct('external_id'))

    # Hack to request
    loop = asyncio.get_event_loop()
    skus, products = loop.run_until_complete(get_skus_and_products_dicts(loop=loop, store=store, vtex=vtex, sc=sc, db_sku_ids=db_sku_ids))

    if products:
        for product in products:
            product_id = product.get('Id')
            if product_id:
                update_or_create_product(store=store, product=product, product_id=product_id, vtex=vtex)
    
    if skus:
        product_instance = None
        for sku_dict in skus:
            product_id = sku_dict.get('ProductId')
            # Get product instance
            if product_id:

                # Reduce runtime for useless request
                if product_id in products_not_found:
                    product_instance = None

                # Getting a product instance if there's not one already
                elif not product_instance:
                    product_instance = Product.objects.filter(store=store, external_id=product_id).last()

                    # Collection products with a bad request
                    if not product_instance:
                        products_not_found.append(product_id)

                # Changing product instance
                elif product_id != product_instance.external_id:
                    product_instance = Product.objects.filter(store=store, external_id=product_id).last()

                    # Collection products with a bad request
                    if not product_instance and product_id not in products_not_found:
                        products_not_found.append(product_id)

                # Create sku
                sku_instance = update_or_create_sku(product_instance=product_instance, product_id=product_id, sku=sku_dict, vtex=vtex, store=store)

                sku_id = int(sku_dict.get('Id'))
                if sku_instance:
                    # Collection skus with a good request
                    if sku_id not in [*skus_created, *skus_not_found]:
                        skus_created.append(sku_id)

                # Collection skus with a bad request
                elif sku_id not in [*skus_created, *skus_not_found]:
                    skus_not_found.append(int(sku_id))

                # Break creation if there's a limit
                if len(products_created) == limit:
                    break

    # Delete skus that don't have a product
    Skus.objects.filter(product=None).delete()

    print(f'No found it //: products: {products_not_found}, skus: {skus_not_found}')

    # Return skus that will be used in other tasks
    return skus_created


def update_products_vtex_store(store):
    """Creation of product available in the store."""

    # Get list of skus in db
    skus = list(Skus.objects.filter(product__store=store).values_list('external_id', flat=True))

    # Product that return a bad status code in the request
    products_not_found = []

    # Skus that return a bad status code in the request
    skus_not_found = []

    # Set up request class
    vtex = VtexStores(store=store)

    # Get Sales channels in db
    sc = list(SaleChannel.objects.filter(store=store).values_list('external_id', flat=True))

    # Hack to request
    loop = asyncio.get_event_loop()
    skus, products = loop.run_until_complete(get_skus_and_products_dicts(loop=loop, store=store, vtex=vtex, sc=sc, skus=skus))

    if products:
        for product in products:
            product_id = product.get('Id')
            if product_id:
                update_or_create_product(store=store, product=product, product_id=product_id, vtex=vtex)

    if skus:
        product_instance = None
        for sku_dict in skus:
            product_id = sku_dict.get('ProductId')
            # Get product instance
            if product_id:

                # Reduce runtime for useless request
                if product_id in products_not_found:
                    product_instance = None

                # Getting a product instance if there's not one already
                elif not product_instance:
                    product_instance = Product.objects.filter(store=store, external_id=product_id).last()

                    # Collection products with a bad request
                    if not product_instance:
                        products_not_found.append(product_id)

                # Changing product instance
                elif product_id != product_instance.external_id:
                    product_instance = Product.objects.filter(store=store, external_id=product_id).last()

                    # Collection products with a bad request
                    if not product_instance and product_id not in products_not_found:
                        products_not_found.append(product_id)

                # Update sku
                update_or_create_sku(product_instance=product_instance, product_id=product_id, sku=sku_dict, vtex=vtex, store=store)

    print(f'No found it //: products: {products_not_found}, skus: {skus_not_found}')

    # Delete skus that don't have a product
    Skus.objects.filter(product=None).delete()
    return True
