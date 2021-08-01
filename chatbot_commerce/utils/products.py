"""list of products with their skus."""

# Models
from chatbot_commerce.products.models.departments import Category, Department
from chatbot_commerce.products.models import Skus, ProductsApiVtex, Price, FixedPrices, Image, DateRange

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores, VtexPriceSku


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
        department = Department.objects.filter(department_id=products.get('DepartmentId')).get()
        category = Category.objects.filter(category_id=products.get('CategoryId'))
        if category:
            category = category.get()
            category_name = category.category_name
        else:
            category_name = ""
        try:
            product_instance, created = ProductsApiVtex.objects.update_or_create(
                product_id=products.get('Id'),
                defaults={
                    'name': products.get('Name'),
                    'department_id': products.get('DepartmentId'),
                    'category_id': products.get('CatgoryId'),
                    'department_name': department.department_name,
                    'category_name': category_name,
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
            products = ProductsApiVtex.objects.filter(product_id=product).first()
            try:
                sku_instance, created = Skus.objects.update_or_create(
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
    # Prices & Images
    vtexprice = VtexPriceSku()
    all_skus_dics = Skus.objects.filter(
        products__in=ProductsApiVtex.objects.all()
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
        price_instance, created = Price.objects.update_or_create(
            sku=sku,
            defaults={
                "list_price": price_dic['listPrice'],
                "cost_price": price_dic['costPrice'],
                "markup": price_dic['markup'],
                "base_price": price_dic['basePrice']
            }
        )
        for fixedprice_dic in price_dic['fixedPrices']:
            fixedprice_instace, created = FixedPrices.objects.update_or_create(
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
                daterange_instance, created = DateRange.objects.update_or_create(
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
            image_instance, created = Image.objects.update_or_create(
                image_id=image_dic.get('Id'),
                sku=sku,
                defaults={
                    'is__main': image_dic,
                    'name': name,
                    'label': image_dic.get('Label'),
                    'archive_id': archive_id
                }
            )
    return print('0k')
