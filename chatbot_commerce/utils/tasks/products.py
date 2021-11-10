"""list of product with their skus."""

# Models
from django.db.models.query import Prefetch
from chatbot_commerce.stores.models import (
    Skus, Product, Price, FixedPrice, DateRange,
    Brand, Category, Department,
    Subcategory, Image, Attribute, AttributeType,
    SaleChannel, Seller, SkuSeller
)
from django.contrib.postgres.search import SearchVector

# Apis
from chatbot_commerce.utils.apis import VtexStores, ShopifyStores

# Utils
import asyncio
import gc


def update_or_create_product(store, product, product_id):
    if store.store_type.name == 'SHOPIFY':
        name = product.get('title')
        if name:
            department = Department.objects.filter(name=product.get('product_type')).last()
            brand = Brand.objects.filter(name=product.get('vendor').strip().capitalize()).last()
            try:
                product_instance, _ = Product.objects.update_or_create(
                    store=store,
                    external_id=product_id,
                    defaults={
                        'name': name,
                        'department': department,
                        'brand': brand,
                        'search': ' '.join([product.get('body_html'), name, *[cat.name for cat in [department, brand] if cat]]),
                        'is_visible': product.get('IsVisible'),
                        'description': product.get('body_html'),
                        'description_short': product.get('handle'),
                        'keywords': product.get('tags'),
                        'title': name,
                        'handle': product.get('handle'),
                        'is_active': product.get('available'),
                        'meta_tag_description': product.get('tags'),
                        'raw_json': product,
                    }
                )
                for image in product.get('images'):
                    image, _ = Image.objects.get_or_create(
                        store=store,
                        image_id=image.get('id'),
                        defaults={
                            'position': image.get('position'),
                            'image_url': image.get('src'),
                            'width': image.get('width'),
                            'height': image.get('height'),
                        }
                    )
                    image.products.add(product_instance)
                for sku in product.get('variants'):
                    update_or_create_sku(product_instance=product_instance, product_id=product_id, store=store, sku=sku)
            except Exception as e:
                error = {
                    'message': e,
                    'product_id': product_id,
                }
                print(error)

    elif store.store_type.name == 'VTEX':
        name = product.get('Name')
        if name:
            department = Department.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('DepartmentId')}"], stores=store).last()
            category = Category.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('CategoryId')}"], store=store).last()
            sub_category = Subcategory.objects.prefetch_related(Prefetch('categories', queryset=Category.objects.filter(store=store), to_attr='q_categories')).filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('CategoryId')}"], category__store=store).last()
            brand = Brand.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product.get('BrandId')}"], stores=store).last()
            if not category:
                if sub_category:
                    category = sub_category.q_categories[-1]
            try:
                product_instance, _ = Product.objects.update_or_create(
                    store=store,
                    external_id=product_id,
                    defaults={
                        'name': name,
                        'department': department,
                        'sub_category': sub_category,
                        'category': category,
                        'brand': brand,
                        'search': ' '.join([name, *[cat.name for cat in [department, category, sub_category, brand] if cat]]),
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

    return None


def update_or_create_sku(product_instance, product_id, sku, store):
    s = []
    extra_data_search = []
    if store.store_type.name == 'SHOPIFY':
        sku_name = sku.get('title')
        sku_name = ' '.join((sku_name, sku.get('sku'),))
        sku_instance, _ = Skus.objects.update_or_create(
            external_id=sku.get('id'),
            product=product_instance,
            defaults={
                'name': sku_name,
                'is_active': sku.get('available'),
                'packaged_width': sku.get('weight'),
                'packaged_weight': sku.get('weight_unit'),
                'total_quantity': sku.get('inventory_quantity'),
                'raw_json': sku
            }
        )
        image = Image.objects.filter(image_id=sku.get('image_id'), store=store).last()
        if image:
            image.skus.add(sku_instance)
        price = sku.get('price')
        if price:
            price_instance, _ = Price.objects.update_or_create(
                sku=sku_instance,
                defaults={
                    "base_price": price,
                    "raw_json": {'price': price, 'formatted_price': sku.get('formatted_price'), 'compare_at_price': sku.get('compare_at_price')}
                }
            )
        sku_specifications_array = sku.get('option_values')
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
        sku_instance.search = ' '.join((product_instance.search, *extra_data_search,))
        sku_instance.save()
        extra_data_search.clear()
        del s

    elif store.store_type.name == 'VTEX':
        # Create or update sku
        try:
            # Get instance
            sku_name = sku.get('NameComplete')
            sku_instance, _ = Skus.objects.update_or_create(
                external_id=sku.get('Id'),
                product=product_instance,
                defaults={
                    'name': sku_name,
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
            sc_ids.clear()
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
            sellers_array.clear()
            price = sku.get('price')
            images_array = sku.get('Images')
            sku_specifications_array = sku.get('SkuSpecifications')
            sku.clear()

            # Create image for sku
            try:
                if images_array:
                    for image_dict in images_array:
                        image_url = image_dict.get('ImageUrl')
                        if image_url:
                            name = image_dict.get('ImageName')
                            image_instance, _ = Image.objects.update_or_create(
                                store=store,
                                image_id=image_dict.get('FileId'),
                                defaults={
                                    'name': name,
                                    'image_url': image_url
                                }
                            )
                            image_instance.skus.add(sku_instance)
                            image_instance.products.add(product_instance)
                        else:
                            print(f'error: {images_array}')
                    images_array.clear()
            except Exception as message:
                print(f'message: {message} imagenes')

            # Create price for sku
            try:
                if price:
                    base_price = price.get('basePrice')
                    price_instance, _ = Price.objects.update_or_create(
                        sku=sku_instance,
                        defaults={
                            "list_price": price.get('listPrice'),
                            "cost_price": price.get('costPrice'),
                            "markup": price.get('markup'),
                            "base_price": base_price,
                            "raw_json": price
                        }
                    )
                    if base_price:
                        s.append(int(base_price))
                    fixed_prices = price.get('fixedPrices')
                    if fixed_prices and price_instance:
                        for fixedprice_dic in fixed_prices:
                            fixedprice_instance, _ = FixedPrice.objects.update_or_create(
                                price=price_instance,
                                trade_policy_id=fixedprice_dic["tradePolicyId"],
                                defaults={
                                    "value": fixedprice_dic["value"],
                                    "list_price": fixedprice_dic["listPrice"],
                                    "min_quantity": fixedprice_dic["minQuantity"],
                                    "raw_json": fixedprice_dic
                                }
                            )
                            daterange_dic = fixedprice_dic.get('dateRange')
                            if daterange_dic and fixedprice_instance:
                                print(daterange_dic)
                                daterange_instance, _ = DateRange.objects.update_or_create(
                                    fixed_price=fixedprice_instance,
                                    defaults={
                                        'date_time_from': daterange_dic.get('from'),
                                        'date_time_to': daterange_dic.get('to'),
                                        "raw_json": daterange_dic
                                    }
                                )
                                fixedprice_instance.save()
                        price_instance.save()

                    price.clear()
                    fixed_prices.clear()
            except Exception as message:
                print(f'message: {message} precios')

            # Create attributes for sku
            try:
                if sku_specifications_array:
                    for dic in sku_specifications_array:
                        name = dic.get('FieldName')
                        attribute_type_instance, _ = AttributeType.objects.get_or_create(
                            store=store,
                            name=name.strip().capitalize()
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
                            values.clear()
                    sku_specifications_array.clear()
                if s:
                    s = ' '.join(s)
                    s_replaced = s.replace(',', ' ').replace('.', ' ')
                    s = ' '.join((s, s_replaced,))
                    # sku_instance.search_attributes = s
                    extra_data_search.append(s)
                if sku_name:
                    extra_data_search.append(sku_name)
                sku_instance.search = ' '.join((product_instance.search, *extra_data_search,))
                sku_instance.save()
                extra_data_search.clear()
                del s
            except Exception as message:
                print(f'message: {message} specificaciones')

        except Exception as e:
            error = {
                'message': e,
                'product_id': product_id,
                'sku_id': sku.get('Id'),
            }
            print(error)

    return None


async def get_skus_and_products_dicts(sc, loop, vtex, skus=[], products_created=[]):
    # Get dicts skus
    asynciofunctions_skus = [loop.run_in_executor(None, vtex.get_sku_context, sku_id, sc_id) for sc_id in sc if sc_id in ['1', 1] for sku_id in skus]
    skus_dicts = [await asynciofunction_sku for asynciofunction_sku in asynciofunctions_skus]
    asynciofunctions_skus.clear()

    # Get dicts products
    product_ids = set([sku_dict.get('ProductId') for sku_dict in skus_dicts if sku_dict.get('ProductId') and sku_dict.get('ProductId') not in products_created])
    asynciofunctions_products = [loop.run_in_executor(None, vtex.product_unit, product_id) for product_id in product_ids]
    product_ids.clear()
    products_dicts = [await asynciofunction_product for asynciofunction_product in asynciofunctions_products]
    asynciofunctions_products.clear()

    # Returning values
    return skus_dicts, products_dicts


def create_products_vtex_store(store, limit=False):
    """Creation of product available in the store."""

    if store.store_type.name == 'VTEX':
        # Set up request class
        vtex = VtexStores(store=store)

        # Get Sales channels in db
        sc = list(SaleChannel.objects.filter(store=store).values_list('external_id', flat=True))
        skus_ids = []
        for sc_id in sc:
            page = 1
            while 1:
                add = vtex.get_list_skus_by_storeid(store_id=sc_id, page=page)
                if add == {} or add == []:
                    break
                skus_ids += add
                page += 1
            if sc_id == 1:
                break

        # Order by new-old
        skus_ids = list(set(skus_ids))
        skus_ids.reverse()

        sub_skus_ids = [skus_ids[i:i+1000] for i in range(0, len(skus_ids), 1000)]
        skus_ids.clear()
        products_created = []
        gc.collect()
        for ids in sub_skus_ids:
            loop = asyncio.new_event_loop()
            skus, products = loop.run_until_complete(get_skus_and_products_dicts(loop=loop, vtex=vtex, sc=sc, skus=ids, products_created=products_created))
            loop.close()
            del loop
            gc.collect()
            print(f'round: skus = {len(skus)}, products = {len(products)}')
            if products:
                for product in products:
                    product_id = product.get('Id')
                    if product_id:
                        update_or_create_product(store=store, product=product, product_id=product_id)
                        if product_id not in products_created:
                            products_created.append(product_id)
            products.clear()
            if skus:
                product_instance = None
                for sku_dict in skus:
                    product_id = sku_dict.get('ProductId')
                    # Get product instance
                    if product_id:

                        # Getting a product instance if there's not one already
                        if not product_instance:
                            product_instance = Product.objects.filter(store=store, external_id=product_id).last()

                        # Changing product instance
                        elif product_id != product_instance.external_id:
                            product_instance = Product.objects.filter(store=store, external_id=product_id).last()

                        if product_instance:
                            # Update sku
                            update_or_create_sku(product_instance=product_instance, product_id=product_id, sku=sku_dict, store=store)
            skus.clear()
            if limit:
                break
        sc.clear()
        sub_skus_ids.clear()
        # Delete skus that don't have a product
        Product.objects.update(search_vector=SearchVector('search'))
        Skus.objects.filter(product=None).delete()
        Skus.objects.update(search_vector=SearchVector('search'))
        gc.collect()
    elif store.store_type.name == 'SHOPIFY':
        shopify = ShopifyStores(store=store)
        array = shopify.product_listings(query_params='limit=100')
        for product_dicts in array:
            for product in product_dicts.get('product_listings'):
                product_id = product.get('product_id')
                if product_id:
                    update_or_create_product(store=store, product=product, product_id=product_id)
    return True
