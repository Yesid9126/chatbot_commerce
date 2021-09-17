# Celery
from celery import Celery

# Models
from chatbot_commerce.products.models import (
    Skus, Attribute, AttributeType,
    Price, FixedPrice, DateRange, Image
)
from chatbot_commerce.stores.models import Store


# Utils
from chatbot_commerce.utils.apis.vtex import VtexPriceSku, VtexStores

app = Celery()


@app.task(name='create_price')
def create_price(store_pk, skus=None):
    store = Store.objects.get(pk=store_pk)
    vtexprice = VtexPriceSku(store=store)
    if skus is None:
        all_skus = Skus.objects.filter(product__store__pk=store.pk).order_by()
    else:
        all_skus = Skus.objects.filter(product__store__pk=store.pk, sku_id__in=skus).order_by()
    print(f'total_skus: {len(all_skus)}')

    prices_created = []
    fixedpirces_created = []
    dateranges_created = []
    for sku in all_skus:
        # Create price for sku
        sku_id = int(sku.sku_id)
        print(f'sku_id: {sku_id}')
        price_dic = vtexprice.price_sku(sku_id=sku_id)
        listprice = price_dic.get('listPrice')
        if listprice:
            price_instance, _ = Price.objects.update_or_create(
                sku=sku,
                defaults={
                    "list_price": listprice,
                    "cost_price": price_dic.get('costPrice'),
                    "markup": price_dic.get('markup'),
                    "base_price": price_dic.get('basePrice')
                }
            )
            prices_created.append(price_instance.pk)
            for fixedprice_dic in price_dic.get('fixedPrices'):
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
                daterange_dic = fixedprice_dic.get('dateRange')
                if daterange_dic:
                    daterange_instance, _ = DateRange.objects.update_or_create(
                        fixed_price=fixedprice_instance,
                        defaults={
                            'date_time_from': daterange_dic.get('from'),
                            'date_time_to': daterange_dic.get('to')
                        }
                    )
                    dateranges_created.append(daterange_instance.pk)
    return True


@app.task(name='create_images')
def create_images(store_pk, skus=None):
    store = Store.objects.get(pk=store_pk)
    vtex = VtexStores(store=store)
    if skus is None:
        all_skus = Skus.objects.filter(product__store__pk=store.pk).order_by()
    else:
        all_skus = Skus.objects.filter(product__store__pk=store.pk, sku_id__in=skus).order_by()
    images_created = []
    print(f'total_skus: {len(all_skus)}')
    for sku in all_skus:
        # Create image for sku
        sku_id = int(sku.sku_id)
        images_array = vtex.image_sku(sku_id=sku_id)
        for image_dic in images_array:
            archive_id = image_dic.get('ArchiveId')
            if archive_id:
                name = image_dic.get('Name')
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
            else:
                print(f'error: {images_array}')
                break
    return True


@app.task(name='create_attributes')
def create_attributes(store_pk, skus=None):
    store = Store.objects.get(pk=store_pk)
    vtex = VtexStores(store=store)
    if skus is None:
        all_skus = Skus.objects.filter(product__store__pk=store.pk).order_by('pk')
    else:
        all_skus = Skus.objects.filter(product__store__pk=store.pk, sku_id__in=skus).order_by('pk')

    attributes_type_created = []
    attributes_created = []
    for sku in all_skus:
        print(f'Hola jeje {sku}')
        sku_id = int(sku.sku_id)
        sku_specifications_array = vtex.get_sku_specifications(sku_id=sku_id)
        if 'status_code' and 'message' not in sku_specifications_array:
            for dic in sku_specifications_array:
                field_id = dic.get('FieldId')
                specifications_field = vtex.get_specifications_field(field_id=field_id)
                name = specifications_field.get('Description')
                if field_id and name:
                    attribute_type_instance, _ = AttributeType.objects.update_or_create(
                        store=store,
                        name=name
                    )
                    attributes_type_created.append(attribute_type_instance.pk)
                    attribute_instance, _ = Attribute.objects.update_or_create(
                        sku=sku,
                        attribute_type=attribute_type_instance,
                        value=dic.get('Text')
                    )
                    attributes_created.append(attribute_instance.pk)
                else:
                    print(f'error attribute in sku_id: {sku}, sku_specification: {dic}, specification_field: {specifications_field}')
        else:
            print(f'error attribute in sku_id: {sku}, sku_specifications: {sku_specifications_array}')
    return True
