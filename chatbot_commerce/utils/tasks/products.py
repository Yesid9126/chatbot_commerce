"""list of product with their skus."""

# Models
from chatbot_commerce.stores.models import (
    Sku, Product, Price, FixedPrice, DateRange,
    Brand, Category, Department,
    Subcategory, Image, Attribute, AttributeType,
    SaleChannel, Seller, SkuSeller
)
from django.contrib.postgres.search import SearchVector
from django.db.models import Q

# Apis
from chatbot_commerce.utils.apis import VtexStores, ShopifyStores

# Django utils
from django.utils import timezone

# Utils
import asyncio
import gc
# from chatbot_commerce.utils.models.bulk_creator import BulkCreator


def update_or_create_product(store, product):
    """Update or create a product."""

    if store.store_type.name == 'VTEX':
        product_id = product.get('Id')

    return product_id


def update_or_create_sku_attributes(store, sku):
    """Update or create a sku."""
    s = []
    extra_data_search = []
    if store.store_type.name == 'SHOPIFY':
        # Create or update sku
        try:
            # Get instance
            sku_name = sku.get('NameComplete')
            sku_instance = Sku.objects.filter(external_id=sku.get('id'), product__store=store).last()
            assert sku_instance, 'Sku not found to Shopify'

            sku_specifications_array = sku.get('option_values')
            # Create attributes for sku
            try:
                if sku_specifications_array:
                    for dic in sku_specifications_array:
                        name = dic.get('name')
                        attribute_type_instance, _ = AttributeType.objects.get_or_create(
                            store=store,
                            name=name.strip().capitalize()
                        )
                        value = dic.get('value')
                        if value:
                            attribute_instance, _ = Attribute.objects.get_or_create(
                                attribute_type=attribute_type_instance,
                                value=value,
                            )
                            attribute_instance.skus.add(sku_instance)
                            s.append(value)
                    sku_specifications_array.clear()
                if s:
                    s = ' '.join(s)
                    s_replaced = s.replace(',', ' ').replace('.', ' ')
                    s = ' '.join((s, s_replaced,))
                    # sku_instance.search_attributes = s
                    extra_data_search.append(s)
                if sku_name:
                    extra_data_search.append(sku_name)
                sku_instance.search = ' '.join((sku_instance.search, *extra_data_search,))
                sku_instance.save(update_fields=['search'])
                extra_data_search.clear()
            except Exception as message:
                print(f'message: {message} specificaciones')
            sku.clear()

        except Exception as e:
            error = {
                'message': e,
                'external_sku_id': sku.get('id'),
            }
            print(error)

    elif store.store_type.name == 'VTEX':
        # Create or update sku
        try:
            # Get instance
            sku_name = sku.get('NameComplete')
            sku_instance = Sku.objects.filter(external_id=sku.get('Id'), product__store=store).last()
            assert sku_instance, 'Sku not found to Vtex'

            # Get Sales channels of sku
            sc_ids = sku.get('SalesChannels')
            sc = SaleChannel.objects.filter(store=store, external_id__in=sc_ids)
            sc_ids.clear()
            sku_instance.sales_channels.add(*sc)

            sku_specifications_array = sku.get('SkuSpecifications')

            # Create attributes for sku
            try:
                if sku_specifications_array:
                    for dic in sku_specifications_array:
                        name = dic.get('FieldName')
                        attribute_type_instance, _ = AttributeType.objects.get_or_create(
                            store=store,
                            name=name
                        )
                        values = dic.get('FieldValues')
                        if values:
                            for value in values:
                                attribute_instance, _ = Attribute.objects.get_or_create(
                                    attribute_type=attribute_type_instance,
                                    value=value,
                                )
                                attribute_instance.skus.add(sku_instance)
                                s.append(value)
                            del values
                    del sku_specifications_array
                if s:
                    s = ' '.join(s)
                    s_replaced = s.replace(',', ' ').replace('.', ' ')
                    s = ' '.join((s, s_replaced,))
                    # sku_instance.search_attributes = s
                    extra_data_search.append(s)
                if sku_name:
                    extra_data_search.append(sku_name)
                sku_instance.search = ' '.join((sku_instance.search, *extra_data_search,))
                sku_instance.save(update_fields=['search'])
                extra_data_search.clear()
            except Exception as message:
                print(f'message: {message} specificaciones')
            del sku

        except Exception as e:
            error = {
                'message': e,
                'external_sku_id': sku.get('Id'),
            }
            print(error)
    return None


async def get_skus_and_products_dicts(sc, loop, vtex, skus=[], products_created=[]):
    # Get dicts skus
    asynciofunctions_skus = [loop.run_in_executor(None, vtex.get_sku_context, sku_id, sc_id) for sc_id in sc if sc_id in ['1', 1] for sku_id in skus]
    skus_dicts = [await asynciofunction_sku for asynciofunction_sku in asynciofunctions_skus]
    del asynciofunctions_skus

    # Get dicts products
    product_ids = set([sku_dict.get('ProductId') for sku_dict in skus_dicts if sku_dict.get('ProductId') and sku_dict.get('ProductId') not in products_created])
    asynciofunctions_products = [loop.run_in_executor(None, vtex.product_unit, product_id) for product_id in product_ids]
    product_ids.clear()
    products_dicts = [await asynciofunction_product for asynciofunction_product in asynciofunctions_products]
    del asynciofunctions_products

    # Returning values
    return skus_dicts, products_dicts


# async def create_extra_data_skus(loop, store, skus=[]):
#     # Get dicts skus
#     asynciofunctions_skus = [loop.run_in_executor(None, update_or_create_sku_attributes, store, sku) for sku in skus]
#     [await asynciofunction_sku for asynciofunction_sku in asynciofunctions_skus]
#     asynciofunctions_skus.clear()


def create_products_store(store, limit=False):
    """Creation of product available in the store."""

    if store.store_type.name == 'VTEX':
        # Set up request class
        vtex = VtexStores(store=store)

        # Get Sales channels in db
        sc = list(SaleChannel.objects.filter(store=store).values_list('external_id', flat=True))
        skus_ids = set()
        for sc_id in sc:
            page = 1
            while 1:
                add = vtex.get_list_skus_by_storeid(store_id=sc_id, page=page)
                if add == {} or add == []:
                    break
                skus_ids |= set(add)
                page += 1
            if sc_id == 1:
                break

        # Order by new-old
        skus_ids = list(skus_ids)
        skus_ids.reverse()
        assert len(skus_ids) > 0, 'No skus found'

        sub_skus_ids = [skus_ids[i:i+10000] for i in range(0, len(skus_ids), 10000)]
        del skus_ids
        products_created = set()

        for ids in sub_skus_ids:
            loop = asyncio.new_event_loop()
            skus, products = loop.run_until_complete(get_skus_and_products_dicts(loop=loop, vtex=vtex, sc=sc, skus=ids, products_created=products_created))
            loop.close()
            del loop
            print(f'round: skus = {len(skus)}, products = {len(products)}')
            if products:
                products_ids = [product.get('Id') for product in products]
                products_external_ids = Product.objects.filter(store=store, external_id__in=products_ids).values_list('external_id', flat=True)
                del products_ids
                bulk_update_products = [
                    Product(
                        store=store,
                        pk=Product.objects.filter(store=store, external_id=product.get('Id')).values_list('pk', flat=True)[0],
                        name=product.get('Name'),
                        department=Department.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('DepartmentId')}"], stores=store).last(),
                        sub_category=Subcategory.objects.select_related('category').filter(external_id=product.get('CategoryId'), category__store=store).last(),
                        category=Subcategory.objects.select_related('category').filter(external_id=product.get('CategoryId'), category__store=store).last().category if Subcategory.objects.filter(
                            external_id=product.get('CategoryId'), category__store=store).exists() else Category.objects.filter(external_id=product.get('CategoryId'), store=store).last(),
                        brand=Brand.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('BrandId')}"], stores=store).last(),
                        search=' '.join(
                            [
                                product.get('Name') or '',
                                *[cat.name for cat in
                                    [
                                        Department.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('DepartmentId')}"], stores=store).last(),
                                        Subcategory.objects.select_related('category').filter(external_id=product.get('CategoryId'), category__store=store).last().category if Subcategory.objects.filter(
                                            external_id=product.get('CategoryId'), category__store=store).exists() else Category.objects.filter(external_id=product.get('CategoryId'), store=store).last(),
                                        Subcategory.objects.select_related('category').filter(external_id=product.get('CategoryId'), category__store=store).last(
                                        ), Brand.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('BrandId')}"], stores=store).last()
                                    ] if cat
                                  ]
                            ]
                        ),
                        link_id=product.get('LinkId'),
                        reference_id=product.get('RefId'),
                        is_visible=product.get('IsVisible'),
                        description=product.get('Description'),
                        description_short=product.get('DescriptionShort'),
                        keywords=product.get('KeyWords'),
                        title=product.get('Title'),
                        is_active=product.get('IsActive'),
                        meta_tag_description=product.get('MetaTagDescription'),
                        show_without_stock=product.get('ShowWithoutStock'),
                        raw_json={**product},
                    )
                    for product in products if product.get('Id') in products_external_ids
                ]
                Product.objects.bulk_update(
                    bulk_update_products,
                    [
                        'name',
                        'department',
                        'sub_category',
                        'category',
                        'brand',
                        'search',
                        'link_id',
                        'reference_id',
                        'is_visible',
                        'description',
                        'description_short',
                        'keywords',
                        'title',
                        'is_active',
                        'meta_tag_description',
                        'show_without_stock',
                        'raw_json',
                    ]
                )
                del bulk_update_products

                bulk_products = [
                    Product(
                        store=store,
                        external_id=product.get('Id'),
                        name=product.get('Name'),
                        department=Department.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('DepartmentId')}"], stores=store).last(),
                        sub_category=Subcategory.objects.select_related('category').filter(external_id=product.get('CategoryId'), category__store=store).last(),
                        category=Subcategory.objects.select_related('category').filter(external_id=product.get('CategoryId'), category__store=store).last().category if Subcategory.objects.filter(
                            external_id=product.get('CategoryId'), category__store=store).exists() else Category.objects.filter(external_id=product.get('CategoryId'), store=store).last(),
                        brand=Brand.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('BrandId')}"], stores=store).last(),
                        search=' '.join(
                            [
                                product.get('Name') or '',
                                *[cat.name for cat in
                                    [
                                        Department.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('DepartmentId')}"], stores=store).last(),
                                        Subcategory.objects.select_related('category').filter(external_id=product.get('CategoryId'), category__store=store).last().category if Subcategory.objects.filter(
                                            external_id=product.get('CategoryId'), category__store=store).exists() else Category.objects.filter(external_id=product.get('CategoryId'), store=store).last(),
                                        Subcategory.objects.select_related('category').filter(external_id=product.get('CategoryId'), category__store=store).last(
                                        ), Brand.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('BrandId')}"], stores=store).last()
                                    ] if cat
                                  ]
                            ]
                        ),
                        link_id=product.get('LinkId'),
                        reference_id=product.get('RefId'),
                        is_visible=product.get('IsVisible'),
                        description=product.get('Description'),
                        description_short=product.get('DescriptionShort'),
                        keywords=product.get('KeyWords'),
                        title=product.get('Title'),
                        is_active=product.get('IsActive'),
                        meta_tag_description=product.get('MetaTagDescription'),
                        show_without_stock=product.get('ShowWithoutStock'),
                        raw_json={**product},
                    )
                    for product in products if product.get('Id') not in products_external_ids
                ]
                Product.objects.bulk_create(bulk_products)
                del bulk_products

                products_created |= set(update_or_create_product(store=store, product=product) for product in products)
                del products
            if skus:
                skus_external_ids = Sku.objects.filter(product__store=store, external_id__in=ids).values_list('external_id', flat=True)

                bulk_update_skus = [
                    Sku(
                        product=Product.objects.filter(store=store, external_id=sku.get('ProductId')).last(),
                        pk=Sku.objects.filter(product__store=store, external_id=sku.get('Id')).values_list('pk', flat=True)[0],
                        name=sku.get('NameComplete'),
                        search=' '.join(
                            [
                                sku.get('NameComplete') if sku.get('NameComplete') else '',
                                Product.objects.only('search').filter(store=store, external_id=sku.get('ProductId')).last().search if Product.objects.filter(store=store, external_id=sku.get('ProductId')).exists() else '',
                                str(sku.get('price').get('basePrice')) if sku.get('price') and sku.get('price').get('basePrice') else ''
                            ]
                        ),
                        is_active=sku.get('IsActive'),
                        ref_id=sku.get('RefId'),
                        packaged_height=sku.get('Height'),
                        packaged_length=sku.get('Length'),
                        packaged_widtht=sku.get('Width'),
                        packaged_weight_unit=sku.get('WeightKg'),
                        is_kit=sku.get('IsKit'),
                        comercial_condition_id=sku.get('CommercialConditionId'),
                        manufacter_code=sku.get('ManufacturerCode'),
                        reference_stock_id=sku.get('ReferenceStockKeepingUnitId'),
                        is_inventoried=sku.get('IsInventoried'),
                        is_transported=sku.get('IsTransported'),
                        total_quantity=sku.get('total_quantity'),
                        raw_json={**sku}
                    )
                    for sku in skus if sku.get('Id') in skus_external_ids
                ]
                Sku.objects.bulk_update(
                    bulk_update_skus,
                    [
                        'product',
                        'name',
                        'search',
                        'is_active',
                        'ref_id',
                        'packaged_height',
                        'packaged_length',
                        'packaged_widtht',
                        'packaged_weight_unit',
                        'is_kit',
                        'comercial_condition_id',
                        'manufacter_code',
                        'reference_stock_id',
                        'is_inventoried',
                        'is_transported',
                        'total_quantity',
                        'raw_json'
                    ]
                )
                del bulk_update_skus

                bulk_skus = [
                    Sku(
                        product=Product.objects.filter(store=store, external_id=sku.get('ProductId')).last(),
                        external_id=sku.get('Id'),
                        name=sku.get('NameComplete'),
                        search=' '.join(
                            [
                                sku.get('NameComplete') if sku.get('NameComplete') else '',
                                Product.objects.only('search').filter(store=store, external_id=sku.get('ProductId')).last().search if Product.objects.filter(store=store, external_id=sku.get('ProductId')).exists() else '',
                                str(sku.get('price').get('basePrice')) if sku.get('price') and sku.get('price').get('basePrice') else ''
                            ]
                        ),
                        is_active=sku.get('IsActive'),
                        ref_id=sku.get('RefId'),
                        packaged_height=sku.get('Height'),
                        packaged_length=sku.get('Length'),
                        packaged_widtht=sku.get('Width'),
                        packaged_weight_unit=sku.get('WeightKg'),
                        is_kit=sku.get('IsKit'),
                        comercial_condition_id=sku.get('CommercialConditionId'),
                        manufacter_code=sku.get('ManufacturerCode'),
                        reference_stock_id=sku.get('ReferenceStockKeepingUnitId'),
                        is_inventoried=sku.get('IsInventoried'),
                        is_transported=sku.get('IsTransported'),
                        total_quantity=sku.get('total_quantity'),
                        raw_json={**sku}
                    )
                    for sku in skus if sku.get('Id') not in skus_external_ids
                ]
                Sku.objects.bulk_create(bulk_skus)
                del bulk_skus

                Product.objects.filter(store=store, name__in=[None, 'None']).delete()
                Sku.objects.filter(Q(product=None)).delete()
                sku_pks = Sku.objects.filter(product__store=store, external_id__in=ids).values_list('pk', flat=True)

                Price.objects.filter(sku__in=sku_pks).delete()
                bulk_price = [
                    Price(
                        sku=Sku.objects.filter(external_id=sku.get('Id'), product__store=store).last(),
                        list_price=sku.get('price').get('listPrice'),
                        cost_price=sku.get('price').get('costPrice'),
                        markup=sku.get('price').get('markup'),
                        base_price=sku.get('price').get('basePrice'),
                        raw_json={**sku.get('price')}
                    )
                    for sku in skus if sku.get('price') not in [False, None] and Sku.objects.filter(external_id=sku.get('Id'), product__store=store).exists()
                ]
                try:
                    Price.objects.bulk_create(bulk_price)
                except Exception:
                    Price.objects.filter(sku__in=sku_pks).delete()
                try:
                    Price.objects.bulk_create(bulk_price)
                except Exception:
                    delete_prices = Price.objects.filter(sku__in=sku_pks)
                    [price.delete() for price in delete_prices]
                try:
                    Price.objects.bulk_create(bulk_price)
                except Exception:
                    pass
                try:
                    for price in bulk_price:
                        try:
                            price.save()
                        except Exception:
                            pass
                except Exception as e:
                    raise Exception(f'This is not working {e}')
                del bulk_price

                prices = Price.objects.only('raw_json').filter(sku__in=sku_pks)
                bulk_fixed_price = [
                    FixedPrice(
                        price=price_instance,
                        trade_policy_id=fixed_price.get('tradePolicyId'),
                        value=fixed_price.get('value'),
                        list_price=fixed_price.get('listPrice'),
                        min_quantity=fixed_price.get('minQuantity'),
                        date_range=DateRange.objects.create(
                            date_time_from=fixed_price.get('dateRange').get('from'),
                            date_time_to=fixed_price.get('dateRange').get('to'),
                            raw_json={**fixed_price.get('dateRange')}
                        ) if fixed_price.get('dateRange') else None,
                        raw_json={**price_instance.raw_json}
                    )
                    for price_instance in prices
                    for fixed_price in price_instance.raw_json.get('fixedPrices')
                ]
                FixedPrice.objects.bulk_create(bulk_fixed_price)
                del bulk_fixed_price

                Sku.objects.filter(product=None).delete()
                skus = Sku.objects.select_related('product').only('product', 'raw_json').filter(pk__in=sku_pks)

                Image.objects.filter(sku__in=sku_pks).delete()
                bulk_image = [
                    Image(
                        sku=sku,
                        product=sku.product,
                        image_id=image_dict.get('FileId'),
                        image_url=image_dict.get('ImageUrl'),
                        name=image_dict.get('ImageName'),
                    )
                    for sku in skus
                    for image_dict in sku.raw_json.get('Images') if sku.raw_json.get('Images')
                ]
                Image.objects.bulk_create(bulk_image)
                del bulk_image

                SkuSeller.objects.filter(sku__in=sku_pks).delete()
                bulk_sku_seller = [
                    SkuSeller(
                        sku=sku,
                        seller=Seller.objects.filter(store=store, seller_id=seller.get('SellerId')).last(),
                        is_active=seller.get('IsActive'),
                        raw_json={**seller}
                    )
                    for sku in skus
                    for seller in sku.raw_json.get('SkuSellers') if sku.raw_json.get('SkuSellers')
                ]
                SkuSeller.objects.bulk_create(bulk_sku_seller)
                del bulk_sku_seller

                [
                    update_or_create_sku_attributes(
                        store=store,
                        sku=sku.raw_json
                    )
                    for sku in skus
                ]

            if limit:
                break
        del sc
        del sub_skus_ids

    elif store.store_type.name == 'SHOPIFY':
        shopify = ShopifyStores(store=store)
        product_array = shopify.product_listings(query_params='limit=250')

        if product_array:
            products_ids = [product.get('product_id') for product in product_array]
            products_external_ids = Product.objects.filter(store=store, external_id__in=products_ids).values_list('external_id', flat=True)
            del products_ids
            [
                Product.objects
                .filter(store=store, external_id=product.get('product_id'))
                .update(
                    name=product.get('title'),
                    department=Department.objects.filter(name=product.get('product_type')).last(),
                    brand=Brand.objects.filter(name=product.get('vendor').strip().capitalize()).last(),
                    search=' '.join(
                        [
                            product.get('body_html'),
                            product.get('title'),
                            *[
                                cat.name for cat in [
                                    Department.objects.filter(name=product.get('product_type')).last(),
                                    Brand.objects.filter(name=product.get('vendor').strip().capitalize()).last()
                                ] if cat
                            ]
                        ]
                    ),
                    is_visible=product.get('IsVisible'),
                    description=product.get('body_html'),
                    description_short=product.get('handle'),
                    keywords=product.get('tags'),
                    title=product.get('Title'),
                    handle=product.get('handle'),
                    is_active=product.get('available'),
                    meta_tag_description=product.get('tags'),
                    modified=timezone.now(),
                    raw_json={**product}
                )
                for product in product_array if product.get('product_id') in products_external_ids
            ]
            bulk_products = [
                Product(
                    store=store,
                    external_id=product.get('product_id'),
                    name=product.get('title'),
                    department=Department.objects.filter(name=product.get('product_type')).last(),
                    brand=Brand.objects.filter(name=product.get('vendor').strip().capitalize()).last(),
                    search=' '.join(
                        [
                            product.get('body_html'),
                            product.get('title'),
                            *[
                                cat.name for cat in [
                                    Department.objects.filter(name=product.get('product_type')).last(),
                                    Brand.objects.filter(name=product.get('vendor').strip().capitalize()).last()
                                ] if cat
                            ]
                        ]
                    ),
                    is_visible=product.get('IsVisible'),
                    description=product.get('body_html'),
                    description_short=product.get('handle'),
                    keywords=product.get('tags'),
                    title=product.get('Title'),
                    handle=product.get('handle'),
                    is_active=product.get('available'),
                    meta_tag_description=product.get('tags'),
                    raw_json={**product}
                )
                for product in product_array if product.get('product_id') not in products_external_ids
            ]
            Product.objects.bulk_create(bulk_products)
            del bulk_products

            product_array = Product.objects.only('raw_json', 'search').filter(store=store)
            variant_ids = [
                variant.get('id')
                for product in product_array if product.raw_json.get('variants')
                for variant in product.raw_json.get('variants')
            ]
            if variant_ids:
                skus_external_ids = Sku.objects.filter(product__store=store, external_id__in=variant_ids).values_list('external_id', flat=True)
                variant_ids.clear()
                [
                    Sku.objects
                    .filter(product__store=store, external_id=variant.get('id'))
                    .update(
                        product=Product.objects.filter(store=store, external_id=product.raw_json.get('product_id')).last(),
                        name='/shopify@@sku/'.join([variant.get('title'), variant.get('sku') if variant.get('sku') else '']),
                        search=' '.join(
                            [
                                variant.get('title'),
                                variant.get('sku') if variant.get('sku') else '',
                                product.search,
                                variant.get('price') if variant.get('price') else ''
                            ]
                        ),
                        is_active=variant.get('available'),
                        packaged_length=variant.get('Length'),
                        packaged_widtht=variant.get('weight'),
                        packaged_weight_unit=variant.get('weight_unit'),
                        total_quantity=variant.get('inventory_quantity'),
                        modified=timezone.now(),
                        raw_json={**variant}
                    )
                    for product in product_array if product.raw_json.get('variants')
                    for variant in product.raw_json.get('variants') if variant.get('id') in skus_external_ids
                ]
                bulk_skus = [
                    Sku(
                        external_id=variant.get('id'),
                        product=Product.objects.filter(store=store, external_id=product.raw_json.get('product_id')).last(),
                        name='/shopify@@sku/'.join([variant.get('title'), variant.get('sku') if variant.get('sku') else '']),
                        search=' '.join(
                            [
                                variant.get('title'),
                                variant.get('sku') if variant.get('sku') else '',
                                product.search,
                                variant.get('price') if variant.get('price') else ''
                            ]
                        ),
                        is_active=variant.get('available'),
                        packaged_length=variant.get('Length'),
                        packaged_widtht=variant.get('weight'),
                        packaged_weight_unit=variant.get('weight_unit'),
                        total_quantity=variant.get('inventory_quantity'),
                        raw_json={**variant}
                    )
                    for product in product_array if product.raw_json.get('variants')
                    for variant in product.raw_json.get('variants') if variant.get('id') not in skus_external_ids
                ]
                Sku.objects.bulk_create(bulk_skus)
                del bulk_skus

                Price.objects.filter(sku__product__store=store).delete()
                variants = Sku.objects.only('raw_json').filter(product__store=store)
                bulk_price = [
                    Price(
                        sku=variant,
                        base_price=variant.raw_json.get('price'),
                        raw_json={
                            'price': variant.raw_json.get('price'),
                            'formatted_price': variant.raw_json.get('formatted_price'),
                            'compare_at_price': variant.raw_json.get('compare_at_price')
                        }
                    )
                    for variant in variants
                ]
                Price.objects.bulk_create(bulk_price)
                del bulk_price

                Image.objects.filter(product__store=store).delete()
                bulk_product_images = [
                    Image(
                        product=product,
                        sku=None,
                        image_id=image.get('id'),
                        position=image.get('position'),
                        image_url=image.get('src'),
                        width=image.get('width'),
                        height=image.get('height'),
                    )
                    for product in product_array if product.raw_json.get('images')
                    for image in product.raw_json.get('images') if not image.get('variant_ids')
                ]
                Image.objects.bulk_create(bulk_product_images)
                del bulk_product_images

                bulk_variant_images = [
                    Image(
                        product=product,
                        sku=Sku.objects.filter(product__store=store, external_id=variant_id).last(),
                        image_id=image.get('id'),
                        position=image.get('position'),
                        image_url=image.get('src'),
                        width=image.get('width'),
                        height=image.get('height'),
                    )
                    for product in product_array if product.raw_json.get('images')
                    for image in product.raw_json.get('images') if image.get('variant_ids')
                    for variant_id in image.get('variant_ids')
                ]
                Image.objects.bulk_create(bulk_variant_images)
                del bulk_variant_images

                [
                    update_or_create_sku_attributes(
                        store=store,
                        sku=variant
                    )
                    for product in product_array if product.raw_json.get('variants')
                    for variant in product.raw_json.get('variants')
                ]

    # Delete skus that don't have a product
    needed()

    return True


def needed():
    Product.objects.update(search_vector=SearchVector('search'))
    Product.objects.filter(name__in=[None, 'None']).delete()
    Sku.objects.filter(product=None).delete()
    Sku.objects.update(search_vector=SearchVector('search'))
    # set(map(lambda sku: sku.get_serializer_data, Sku.objects.all()))
