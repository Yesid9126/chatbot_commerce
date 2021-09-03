# Celery
from celery.task import task

# Models
from chatbot_commerce.products.models import (
    Skus, Product, Attribute, AttributeType,
    Price, FixedPrice, DateRange, Image
)
from chatbot_commerce.stores.models import Store


# Utils
from chatbot_commerce.utils.apis.vtex import VtexPriceSku, VtexStores


@task(name='create_price')
def create_price(store, skus=None):
    store = Store.objects.filter(name=store).first()
    vtexprice = VtexPriceSku(store=store)
    if skus is None:
        all_skus = Skus.objects.filter(
            product__pk__in=Product.objects.filter(store=store).order_by().values_list('pk', flat=True)
        ).order_by().values_list('sku_id', flat=True)
    else:
        all_skus = skus
    print(f'total_skus: {len(all_skus)}')
    prices_created = []
    fixedpirces_created = []
    dateranges_created = []

    for sku in all_skus:
        # Create price for sku
        sku_id = int(sku)
        print(f'sku_id: {sku_id}')
        price_dic = vtexprice.price_sku(sku_id=sku_id)
        if 'listPrice' in price_dic:
            price_instance, _ = Price.objects.update_or_create(
                sku=Skus.objects.filter(sku_id=sku_id).first(),
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
    return True


@task(name='create_images')
def create_images(store, skus=None):
    store = Store.objects.filter(name=store).first()
    vtex = VtexStores(store=store)
    product_pks = Product.objects.filter(store=store).order_by().values_list('pk', flat=True)
    if skus is None:
        all_skus = Skus.objects.filter(
            product__pk__in=product_pks
        ).order_by().values_list('sku_id', flat=True)
    else:
        all_skus = skus
    images_created = []
    print(f'total_skus: {len(all_skus)}')
    for sku in all_skus:
        # Create image for sku
        sku_id = int(sku)
        images_array = vtex.image_sku(sku_id=sku_id)
        for image_dic in images_array:
            if 'ArchiveId' in image_dic:
                archive_id = image_dic['ArchiveId']
                name = image_dic['Name']
                image_instance, _ = Image.objects.update_or_create(
                    image_id=image_dic.get('Id'),
                    sku=Skus.objects.filter(sku_id=sku_id, product__pk__in=product_pks).first(),
                    defaults={
                        'is_main': image_dic.get('IsMain'),
                        'name': name,
                        'label': image_dic.get('Label'),
                        'archive_id': archive_id
                    }
                )
                images_created.append(image_instance.pk)
    return True


@task(name='create_attributes')
def create_attributes(store, skus=None):
    store = Store.objects.filter(name=store).first()
    vtex = VtexStores(store=store)
    if skus is None:
        all_skus = Skus.objects.filter(
            product__pk__in=Product.objects.filter(store=store).order_by().values_list('pk', flat=True)
        ).order_by().values_list('sku_id', flat=True)
    else:
        all_skus = skus
    attributes_type_created = []
    attributes_created = []

    for sku in all_skus:
        sku_id = int(sku)
        sku_specifications_array = vtex.get_sku_specifications(sku_id=sku_id)
        if 'status_code' and 'message' not in sku_specifications_array:
            for dic in sku_specifications_array:
                specifications_field = vtex.get_specifications_field(field_id=dic.get('FieldId'))
                if 'status_code' and 'message' not in specifications_field:
                    try:
                        attribute_type_instance, _ = AttributeType.objects.update_or_create(
                            store=store,
                            name=specifications_field.get('Description')
                        )
                        attributes_type_created.append(attribute_type_instance.pk)
                        attribute_instance, _ = Attribute.objects.update_or_create(
                            sku=Skus.objects.filter(sku_id=sku_id).first(),
                            attribute_type=attribute_type_instance,
                            value=dic.get('Text')
                        )
                        attributes_created.append(attribute_instance.pk)
                    except Exception as e:
                        error = {
                            'message': e,
                            'FieldId': dic.get('FieldId'),
                            'name': specifications_field,
                            'sku_specification': dic
                        }
                        print(error)
                        raise Exception(error)
                else:
                    print(f'error attribute in sku_id: {sku}, sku_specification: {dic}, specification_field: {specifications_field}')
        else:
            print(f'error attribute in sku_id: {sku}, sku_specifications: {sku_specifications_array}')
    return True
