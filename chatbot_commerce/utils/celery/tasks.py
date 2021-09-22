# Celery
from celery import Celery

# Models
from chatbot_commerce.products.models import (
    Skus, Attribute, AttributeType,
    Price, FixedPrice, DateRange, Image
)
from chatbot_commerce.stores.models import Store


# Utils
from chatbot_commerce.utils.apis.vtex import VtexPriceSku

app = Celery()


@app.task(name='create_price')
def create_price(store_pk, skus=None):
    store = Store.objects.get(pk=store_pk)
    vtexprice = VtexPriceSku(store=store)
    if skus is None:
        all_skus = Skus.objects.filter(product__store=store)
    else:
        all_skus = Skus.objects.filter(product__store=store, external_id__in=skus)
    print(f'total_skus: {len(all_skus)}')

    prices_created = []
    fixedpirces_created = []
    dateranges_created = []
    for sku in all_skus:
        # Create price for sku
        sku_id = int(sku.external_id)
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
                    "base_price": price_dic.get('basePrice'),
                    "raw_json": price_dic
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
                        "min_quantity": fixedprice_dic["minQuantity"],
                        "raw_json": fixedprice_dic
                    }
                )
                fixedpirces_created.append(fixedprice_instance.pk)
                daterange_dic = fixedprice_dic.get('dateRange')
                if daterange_dic:
                    daterange_instance, _ = DateRange.objects.update_or_create(
                        fixed_price=fixedprice_instance,
                        defaults={
                            'date_time_from': daterange_dic.get('from'),
                            'date_time_to': daterange_dic.get('to'),
                            "raw_json": daterange_dic
                        }
                    )
                    dateranges_created.append(daterange_instance.pk)
    return True

def create_images(store, skus=None):
    if skus is None:
        all_skus = Skus.objects.filter(product__store=store)
    else:
        all_skus = Skus.objects.filter(product__store=store, external_id__in=skus)
    images_created = []
    print(f'total_skus: {len(all_skus)}')
    for sku in all_skus:
        # Create image for sku
        sku_dict = sku.raw_json
        images_array = sku_dict.get('Images')
        for image_dict in images_array:
            image_url = image_dict.get('ImageUrl')
            if image_url:
                name = image_dict.get('ImageName')
                image_instance, _ = Image.objects.update_or_create(
                    image_id=image_dict.get('FileId'),
                    sku=sku,
                    defaults={
                        'name': name,
                        'image_url': image_url
                    }
                )
                images_created.append(image_instance.pk)
            else:
                print(f'error: {images_array}')
                break
    return True

def create_attributes(store, skus=None):
    print('create_attributes')
    if skus is None:
        all_skus = Skus.objects.filter(product__store=store)
    else:
        all_skus = Skus.objects.filter(product__store=store, external_id__in=skus)

    for sku in all_skus:
        sku_dict = sku.raw_json
        sku_specifications_array = sku_dict.get('SkuSpecifications')
        for dic in sku_specifications_array:
            name = dic.get('FieldName')
            attribute_type_instance, _ = AttributeType.objects.get_or_create(
                store=store,
                name=name
            )
            values = dic.get('FieldValues')
            for value in values:
                attribute_instance, _ = Attribute.objects.update_or_create(
                    sku=sku,
                    attribute_type=attribute_type_instance,
                    value=value,
                )
    return True
