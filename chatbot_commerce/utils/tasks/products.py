"""list of product with their skus."""

# Models
from chatbot_commerce.stores.models import (
    Sku, Product, Price, FixedPrice, DateRange,
    Brand, Category, Department,
    Subcategory, Image, Attribute, AttributeType,
    Seller, SkuSeller
)
from django.contrib.postgres.search import SearchVector

# Apis
from chatbot_commerce.utils.apis import VtexStores, VtexApi

# Django Models
from django.db.models import Q, F, Value, TextField
from django.db.models.functions import Concat

# Utils
import asyncio

def create_products_store(store, limit=False):
    """Creation of product available in the store."""

    if store.store_type.name == 'VTEX':
        # Set up request class
        vtex = VtexApi(store=store)
        vtex_store = VtexStores(store=store)

        # Get Sales channels in db
        response = vtex_store.get_product_ids_with_sku_ids(from_position=1, to_position=1)
        data = response.get('data')
        vtex_product_ids = []
        vtex_sku_ids = []
        if data:
            total_products = response.get('range').get('total')
        else:
            total_products = 0
        for to_position in range(51, total_products + 51, 51):
            from_position = to_position - 50
            response = vtex_store.get_product_ids_with_sku_ids(from_position, to_position)
            data = response.get('data')
            if not data:
                break
            vtex_product_ids.extend(data.keys())
            for product_id, sku_ids in data.items():
                vtex_sku_ids.extend(sku_ids)

        if vtex_product_ids:
            Product.objects.filter(~Q(external_id__in=vtex_product_ids), store=store).delete()
            vtex_product_ids = [vtex_product_ids[i:i+5000] for i in range(0, len(vtex_product_ids), 5000)]
            for vtex_product_id_list in vtex_product_ids:
                loop = asyncio.get_event_loop()
                future = asyncio.ensure_future(vtex.get_products(vtex_product_id_list))
                product_responses = loop.run_until_complete(future)
                # [
                #     Product.objects.update_or_create(
                #         store=store,
                #         external_id=product_response.get('Id'),
                #         defaults={
                #             'name': product_response.get('Name'),
                #             'department': Department.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product_response.get('DepartmentId')}"], stores=store).last(),
                #             'sub_category': Subcategory.objects.select_related('category').filter(external_id=product_response.get('CategoryId'), category__store=store).last(),
                #             'category': Subcategory.objects.select_related('category').filter(external_id=product_response.get('CategoryId'), category__store=store).last().category if Subcategory.objects.filter(
                #                 external_id=product_response.get('CategoryId'), category__store=store).exists() else Category.objects.filter(external_id=product_response.get('CategoryId'), store=store).last(),
                #             'brand': Brand.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product_response.get('BrandId')}"], stores=store).last(),
                #             'link_id': product_response.get('LinkId'),
                #             'reference_id': product_response.get('RefId'),
                #             'is_visible': product_response.get('IsVisible'),
                #             'description': product_response.get('Description'),
                #             'description_short': product_response.get('DescriptionShort'),
                #             'keywords': product_response.get('KeyWords'),
                #             'title': product_response.get('Title'),
                #             'is_active': product_response.get('IsActive'),
                #             'meta_tag_description': product_response.get('MetaTagDescription'),
                #             'show_without_stock': product_response.get('ShowWithoutStock'),
                #             'raw_json': {**product_response}
                #         }
                #     )
                #     for product_response in product_responses if product_response.get('Id')
                # ]
                del product_responses
            del vtex_product_ids

        if vtex_sku_ids:
            Sku.objects.filter(~Q(external_id__in=vtex_sku_ids), product__store=store).delete()
            vtex_sku_ids = [vtex_sku_ids[i:i+5000] for i in range(0, len(vtex_sku_ids), 5000)]
            for vtex_sku_id_list in vtex_sku_ids:
                loop = asyncio.get_event_loop()
                future = asyncio.ensure_future(vtex.get_skus(vtex_sku_id_list))
                sku_responses = loop.run_until_complete(future)

                for sku_response in sku_responses:
                    s = []
                    instance_product = Product.objects.filter(external_id=sku_response.get('ProductId'), store=store).last()
                    if not instance_product or not sku_response.get('Id'):
                        continue
                    instance_sku, _is_new = Sku.objects.update_or_create(
                        product=instance_product,
                        external_id=sku_response.get('Id'),
                        defaults={
                            'name': sku_response.get('NameComplete'),
                            'is_active': sku_response.get('IsActive'),
                            'ref_id': sku_response.get('RefId'),
                            'packaged_height': sku_response.get('Height'),
                            'packaged_length': sku_response.get('Length'),
                            'packaged_widtht': sku_response.get('Width'),
                            'packaged_weight_unit': sku_response.get('WeightKg'),
                            'is_kit': sku_response.get('IsKit'),
                            'comercial_condition_id': sku_response.get('CommercialConditionId'),
                            'manufacter_code': sku_response.get('ManufacturerCode'),
                            'reference_stock_id': sku_response.get('ReferenceStockKeepingUnitId'),
                            'is_inventoried': sku_response.get('IsInventoried'),
                            'is_transported': sku_response.get('IsTransported'),
                            'raw_json': {**sku_response}
                        }
                    )
                    sku_specifications = sku_response.get('SkuSpecifications') or []
                    for sku_specification in sku_specifications:
                        attribute_type_instance, _ = AttributeType.objects.get_or_create(
                            store=store,
                            name=sku_specification.get('FieldName')
                        )
                        values = sku_specification.get('FieldValues')
                        if values: s.append(sku_specification.get('FieldName'))
                        for value in values:
                            attribute_instance, _ = Attribute.objects.get_or_create(
                                attribute_type=attribute_type_instance,
                                value=value,
                            )
                            attribute_instance.skus.add(instance_sku)
                            s.append(value)
                    if s:
                        s = ' '.join(s)
                        s_replaced = s.replace(',', ' ').replace('.', ' ')
                        s = [' '.join((s, s_replaced,))]
                    categories = sku_response.get('ProductCategories').values() if sku_response.get('ProductCategories') else []
                    search = ' '.join(
                        [
                            text
                            for text in [
                                sku_response.get('BrandName'),
                                *categories,
                                sku_response.get('SkuName'),
                                sku_response.get('ProductName'),
                                sku_response.get('ComplementName'),
                                sku_response.get('NameComplete'),
                                *s,
                                *categories,
                                sku_response.get('BrandName'),
                                *categories,
                            ] if text
                        ]
                    )
                    instance_sku.search = search
                    instance_sku.save(update_fields=['search'])
                    images = sku_response.get('Images')
                    if images:
                        [
                            Image.objects.update_or_create(
                                product=instance_product,
                                sku=instance_sku,
                                image_id=image.get('FileId'),
                                defaults={'name': image.get('ImageName'), 'image_url': image.get('ImageUrl')}
                            )
                            for image in images
                        ]
                    sku_sellers = sku_response.get('SkuSellers')
                    if sku_sellers:
                        [
                            SkuSeller.objects.update_or_create(
                                sku=instance_sku,
                                seller=Seller.objects.filter(store=store, seller_id=sku_seller.get('SellerId')).last(),
                                defaults={
                                    'is_active': sku_seller.get('IsActive'),
                                    'raw_json': {**sku_seller}
                                }
                            )
                            for sku_seller in sku_sellers
                        ]
                    if limit:
                        break
                del sku_responses

                loop = asyncio.get_event_loop()
                future = asyncio.ensure_future(vtex.get_sku_prices(vtex_sku_id_list))
                sku_price_responses = loop.run_until_complete(future)
                for sku_price_response in sku_price_responses:
                    instance_sku = Sku.objects.filter(external_id=sku_price_response.get('itemId'), product__store=store).last()
                    if not instance_sku or not sku_price_response.get('itemId'):
                        continue
                    Price.objects.update_or_create(
                        sku=instance_sku,
                        defaults={
                            'list_price': sku_price_response.get('listPrice'),
                            'cost_price': sku_price_response.get('costPrice'),
                            'markup': sku_price_response.get('markup'),
                            'base_price': sku_price_response.get('basePrice'),
                            'raw_json': {**sku_price_response}
                        }
                    )
                    if limit:
                        break
                del sku_price_responses

                loop = asyncio.get_event_loop()
                future = asyncio.ensure_future(vtex.get_sku_inventories(vtex_sku_id_list))
                sku_inventory_responses = loop.run_until_complete(future)
                for sku_inventory_response in sku_inventory_responses:
                    instance_sku = Sku.objects.filter(external_id=sku_inventory_response.get('skuId'), product__store=store).last()
                    if not instance_sku or not sku_inventory_response.get('skuId'):
                        continue
                    balances = sku_inventory_response.get('balance')
                    if balances:
                        total_quantity = 0
                        for balance in balances:
                            total_quantity += balance.get('totalQuantity')

                        instance_sku.total_quantity = total_quantity
                        instance_sku.save(update_fields=['total_quantity'])
                    if limit:
                        break
                del sku_inventory_responses

    # Delete skus that don't have a product
    Sku.objects.filter(product__store=store).update(search_vector=SearchVector('search'))
    needed()

    return True


def needed():
    Product.objects.filter(name__in=[None, 'None']).delete()
    Sku.objects.filter(product=None).delete()
    # set(map(lambda sku: sku.get_serializer_data, Sku.objects.all()))
