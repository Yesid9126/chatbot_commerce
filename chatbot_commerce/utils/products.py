"""list of product with their skus."""

# Models
from chatbot_commerce.products.models import (
    Skus, Product, Price,
    FixedPrice, Image, DateRange,
    Brand, Category, Department,
    Subcategory,
)
from chatbot_commerce.stores.models import Store

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores, VtexPriceSku


def get_products_vtex_store():
    """Creation of product available in the store."""
    products_created = []
    skus_created = []
    vtex = VtexStores()
    skus = vtex.total_skus()
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
        department = Department.objects.filter(external_id=product.get('DepartmentId')).last()
        category = Category.objects.filter(external_id=product.get('CategoryId')).last()
        if not category:
            sub_category = Subcategory.objects.filter(external_id=product.get('CategoryId')).last()
            category = sub_category.category
        try:
            product_instance, _ = Product.objects.update_or_create(
                store=Store.objects.last(),
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
            print(e)
    # Create skus for product
    for product_key in products_skus:
        product = Product.objects.filter(external_id=product_key).first()
        skus_product = vtex.Product_skus(product_id=product_key)
        for skus in skus_product:
            try:
                sku_instance, _ = Skus.objects.update_or_create(
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
                        'product': product,
                        'sku_json': skus
                    }
                )
                skus_created.append(sku_instance.pk)
            except Exception as e:
                error = e
                print(error)
    # Delete product not in store
    Product.objects.all().exclude(pk__in=products_created)
    # Delete sku not in product
    Skus.objects.all().exclude(pk__in=skus_created)

    # Prices & Images
    vtexprice = VtexPriceSku()
    all_skus_dics = Skus.objects.filter(
        product__in=Product.objects.all()
    )\
        .values_list('sku_json', flat=True)
    for sku_dic in all_skus_dics:
        sku = Skus.objects.filter(sku_id=sku_dic.get('Id'), product_id=sku_dic.get('ProductId')).first()
        # Create price for sku
        price_dic = vtexprice.price_sku(sku_id=sku_dic.get('Id'))
        if 'listPrice' not in price_dic:
            price = Price.objects.filter(sku=sku).first()
            if price:
                price.delete()
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
        for fixedprice_dic in price_dic['fixedPrices']:
            fixedprice_instace, _ = FixedPrice.objects.update_or_create(
                price=price_instance,
                trade_policy_id=fixedprice_dic["tradePolicyId"],
                defaults={
                    "value": fixedprice_dic["value"],
                    "list_price": fixedprice_dic["listPrice"],
                    "min_quantity": fixedprice_dic["minQuantity"]
                }
            )
            if 'dateRange' in fixedprice_dic:
                daterange_dic = fixedprice_dic.get('dateRange')
                DateRange.objects.update_or_create(
                    fixed_price=fixedprice_instace,
                    defaults={
                        'date_time_from': daterange_dic.get('from'),
                        'date_time_to': daterange_dic.get('to')
                    }
                )
                continue
            date_ranges = DateRange.objects.filter(fixed_price=fixedprice_instace)
            if date_ranges:
                date_ranges.delete()
        # Create image for sku
        images_array = vtex.image_sku(sku_id=sku_dic.get('Id'))
        images = Image.objects.filter(sku=sku)
        if len(images_array) != images.count():
            images.delete()
        for image_dic in images_array:
            if 'ArchiveId' not in image_dic:
                if images:
                    images.delete()
                break
            archive_id = image_dic['ArchiveId']
            name = image_dic['Name']
            Image.objects.update_or_create(
                image_id=image_dic.get('Id'),
                sku=sku,
                defaults={
                    'is_main': image_dic.get('IsMain'),
                    'name': name,
                    'label': image_dic.get('Label'),
                    'archive_id': archive_id
                }
            )
    return print('0k')
