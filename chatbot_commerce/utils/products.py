"""list of products with their skus."""

# Models
from chatbot_commerce.products.models.departments import Category, Department
from chatbot_commerce.products.models import Skus, ProductsApiVtex, Price, FixedPrices, Image
from chatbot_commerce.stores.models import StoresVtex

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
            products, created = ProductsApiVtex.objects.update_or_create(
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
                product, created = Skus.objects.update_or_create(
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
    store = StoresVtex.objects.filter(name='pilatos').get()
    all_skus_dics = Skus.objects.all().values_list('sku_json', flat=True)
    for sku_dic in all_skus_dics:
        sku = Skus.objects.filter(sku_id=sku_dic.get('Id'), product_id=sku_dic.get('ProductId')).first()
        # Create price for sku
        price_dic = vtexprice.price_sku(sku_id=sku_dic.get('Id'))
        if 'listPrice' not in price_dic:
            price = Price.objects.filter(sku=sku, store=store).first()
            if price:
                price.delete()
            continue
        price_instance, created = Price.objects.update_or_create(
            sku=sku,
            store=store,
            defaults={
                "listPrice": price_dic['listPrice'],
                "costPrice": price_dic['costPrice'],
                "markup": price_dic['markup'],
                "basePrice": price_dic['basePrice']
            }
        )
        for fixedprice_dic in price_dic['fixedPrices']:
            fixedprice_instace, created = FixedPrices.objects.update_or_create(
                price=price_instance,
                store=store,
                tradePolicyId=fixedprice_dic["tradePolicyId"],
                defaults={
                    "value": fixedprice_dic["value"],
                    "listPrice": fixedprice_dic["listPrice"],
                    "minQuantity": fixedprice_dic["minQuantity"]
                }
            )
        # Create image for sku
        images_array = vtex.image_sku(sku_id=sku_dic.get('Id'))
        images = Image.objects.filter(Sku=sku, store=store, SkuId=sku_dic.get('Id'))
        if len(images_array) != images.count():
            images.delete()
        for image_dic in images_array:
            if 'ArchiveId' not in image_dic:
                if images:
                    images.delete()
                break
            num = image_dic['ArchiveId']
            name = image_dic['Name']
            image_dic['image_url'] = f'https://{store.name}.vteximg.com.br/arquivos/ids/{num}/{name}.jpg'
            updated, created = Image.objects.update_or_create(
                Id=image_dic.get('Id'),
                Sku=sku,
                SkuId=sku_dic.get('Id'),
                store=store,
                defaults=image_dic
            )
    return print('0k')
