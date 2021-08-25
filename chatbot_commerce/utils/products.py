"""list of product with their skus."""

# Models
from chatbot_commerce.products.models import (
    Skus, Product, Price,
    FixedPrice, Image, DateRange,
    Brand, Category, Department,
    Subcategory, AttributeType,
    Attribute
)

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores, VtexPriceSku


def get_products_vtex_store(store):
    """Creation of product available in the store."""
    products_created = []
    skus_created = []
    prices_created = []
    fixedpirces_created = []
    images_created = []
    dateranges_created = []
    attributes_type_created = []
    attributes_created = []

    vtex = VtexStores()
    skus = []
    page = 1
    while True:
        skus_ids = vtex.total_skus(page=page)
        if page == 2:
            break
        skus += skus_ids
        page += 1
    products_skus = []
    if skus:
        for sku_unit in skus:
            sku = sku_unit
            product_id = vtex.unit_sku(sku=sku)
            product_id = product_id.get('ProductId')
            if product_id not in products_skus:
                products_skus.append(product_id)
    for product in products_skus:
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
    for product_key in products_skus:
        product = Product.objects.filter(external_id=product_key, store=store).first()
        skus_product = vtex.product_skus(product_id=product_key)
        for skus in skus_product:
            total_quantity = 0
            try:
                skus_inventory = vtex.skus_inventory(sku_id=skus.get('Id'))
                sku_inventory = skus_inventory['balance']
                for quantity in sku_inventory:
                    quantity_sku = quantity.get('totalQuantity')
                    total_quantity += quantity_sku
            except Exception as e:
                error = e
                print(error)
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
                skus_created.append(sku_instance.pk)
            except Exception as e:
                import ipdb
                ipdb.set_trace()
                error = {
                    'message': e,
                    'product_id': product_key,
                    'sku_id': skus.get('Id'),
                }
                print(error)
    # Delete product not in store
    Product.objects.filter(store=store).exclude(pk__in=products_created).delete()
    # Delete sku not in product
    Skus.objects.filter(product__in=Product.objects.filter(store=store)).exclude(pk__in=skus_created).delete()

    # Prices & Images
    vtexprice = VtexPriceSku()
    all_skus = Skus.objects.filter(
        product__in=Product.objects.filter(store=store)
    )
    for sku in all_skus:
        # Create price for sku
        price_dic = vtexprice.price_sku(sku_id=sku.sku_json.get('Id'))
        if 'listPrice' not in price_dic:
            continue
        price_instance, _ = Price.objects.update_or_create(
            sku=sku,
            defaults={
                "list_price": price_dic['listPrice'],
                "cost_price": price_dic['costPrice'],
                "markup": price_dic['markup'],
                "base_price": price_dic['basePrice']
            }
        )
        prices_created.append(price_instance.pk)
        for fixedprice_dic in price_dic['fixedPrices']:
            fixedprice_instance, _ = FixedPrice.objects.update_or_create(
                price=price_instance,
                trade_policy_id=fixedprice_dic["tradePolicyId"],
                defaults={
                    "value": fixedprice_dic["value"],
                    "list_price": fixedprice_dic["listPrice"],
                    "min_quantity": fixedprice_dic["minQuantity"]
                }
            )
            fixedpirces_created.append(fixedprice_instance.pk)
            if 'dateRange' in fixedprice_dic:
                daterange_dic = fixedprice_dic.get('dateRange')
                daterange_instance, _ = DateRange.objects.update_or_create(
                    fixed_price=fixedprice_instance,
                    defaults={
                        'date_time_from': daterange_dic.get('from'),
                        'date_time_to': daterange_dic.get('to')
                    }
                )
                dateranges_created.append(daterange_instance.pk)
        # Create image for sku
        images_array = vtex.image_sku(sku_id=sku.sku_json.get('Id'))
        for image_dic in images_array:
            if 'ArchiveId' not in image_dic:
                continue
            archive_id = image_dic['ArchiveId']
            name = image_dic['Name']
            image_instance, _ = Image.objects.update_or_create(
                image_id=image_dic.get('Id'),
                sku=sku,
                defaults={
                    'is_main': image_dic.get('IsMain'),
                    'name': name,
                    'label': image_dic.get('Label'),
                    'archive_id': archive_id
                }
            )
            images_created.append(image_instance.pk)
        sku_specifications_array = vtex.get_sku_specifications(sku_id=sku.sku_json.get('Id'))
        if 'status_code' and 'message' in sku_specifications_array:
            continue
        for dic in sku_specifications_array:
            specifications_field = vtex.get_specifications_field(field_id=dic.get('FieldId'))
            try:
                attribute_type_instance, _ = AttributeType.objects.update_or_create(
                    store=store,
                    name=specifications_field.get('Description')
                )
                attributes_type_created.append(attribute_type_instance.pk)
                attribute_instance, _ = Attribute.objects.update_or_create(
                    sku=sku,
                    attribute_type=attribute_type_instance,
                    value=dic.get('Text')
                )
                attributes_created.append(attribute_instance.pk)
            except Exception as e:
                error = {
                    'message': e,
                    'FieldId': dic.get('FieldId'),
                    'name': specifications_field.get('Description'),
                    'sku_specification': dic
                }
                print(error)
                raise Exception(error)

    # Delete images not in sku
    Image.objects.filter(sku__in=all_skus).exclude(pk__in=images_created).delete()
    # Delete prices that not exists
    Price.objects.filter(sku__in=all_skus).exclude(pk__in=prices_created).delete()
    # Delete fixedprices not in prices
    FixedPrice.objects.filter(
        price__in=Price.objects.filter(
            sku__in=all_skus
        )
    ).exclude(pk__in=fixedpirces_created).delete()
    # Delete dateranges not in fixedprices
    DateRange.objects.filter(
        fixed_price__in=FixedPrice.objects.filter(
            price__in=Price.objects.filter(
                sku__in=all_skus)
        )
    ).exclude(pk__in=dateranges_created).delete()
    # Delete attributes type that not exists
    AttributeType.objects.filter(
        attributes__in=Attribute.objects.filter(
            sku__in=all_skus
        )
    ).distinct().exclude(pk__in=attributes_type_created).delete()
    # Delete attributes that not exists
    Attribute.objects.filter(sku__in=all_skus).exclude(pk__in=attributes_created).delete()
    return print('0k')
