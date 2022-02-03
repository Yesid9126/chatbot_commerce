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
from chatbot_commerce.utils.apis import VtexStores

# Django Models
from django.db.models import F, Value, TextField
from django.db.models.functions import Concat

# Utils
from math import ceil

def create_products_store(store, limit=False):
    """Creation of product available in the store."""

    if store.store_type.name == 'VTEX':
        # Set up request class
        vtex = VtexStores(store=store)

        # Get Sales channels in db
        response = vtex.get_product_ids_with_sku_ids(from_position=1, to_position=1)
        data = response.get('data')
        if data:
            total_products = response.get('range').get('total')
        for to_position in range(51, total_products + 51, 51):
            from_position = to_position - 50
            response = vtex.get_product_ids_with_sku_ids(from_position, to_position)
            data = response.get('data')
            if not data:
                break
            for product_id, sku_ids in data.items():
                product_response = vtex.product_unit(product_id)
                instance_product, _is_new = Product.objects.update_or_create(
                    store=store,
                    external_id=product_id,
                    defaults={
                        'name': product_response.get('Name'),
                        'department': Department.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product_response.get('DepartmentId')}"], stores=store).last(),
                        'sub_category': Subcategory.objects.select_related('category').filter(external_id=product_response.get('CategoryId'), category__store=store).last(),
                        'category': Subcategory.objects.select_related('category').filter(external_id=product_response.get('CategoryId'), category__store=store).last().category if Subcategory.objects.filter(
                            external_id=product_response.get('CategoryId'), category__store=store).exists() else Category.objects.filter(external_id=product_response.get('CategoryId'), store=store).last(),
                        'brand': Brand.objects.filter(external_id__contains=[f"{store.store_type.name}{store.name}{product_response.get('BrandId')}"], stores=store).last(),
                        'link_id': product_response.get('LinkId'),
                        'reference_id': product_response.get('RefId'),
                        'is_visible': product_response.get('IsVisible'),
                        'description': product_response.get('Description'),
                        'description_short': product_response.get('DescriptionShort'),
                        'keywords': product_response.get('KeyWords'),
                        'title': product_response.get('Title'),
                        'is_active': product_response.get('IsActive'),
                        'meta_tag_description': product_response.get('MetaTagDescription'),
                        'show_without_stock': product_response.get('ShowWithoutStock'),
                        'raw_json': {**product_response}
                    }
                )
                instance_product.save(update_fields=['search'])
                for sku_id in sku_ids:
                    s = []
                    sku_response = vtex.get_sku_context(sku_id)
                    instance_sku, _is_new = Sku.objects.update_or_create(
                        product=instance_product,
                        external_id=sku_id,
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
                            'total_quantity': sku_response.get('total_quantity'),
                            'raw_json': {**sku_response}
                        }
                    )
                    sku_specifications = sku_response.get('SkuSpecifications')
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
                    search = ' '.join(
                        [
                            text
                            for text in [
                                sku_response.get('BrandName'),
                                *sku_response.get('ProductCategories').values(),
                                sku_response.get('SkuName'),
                                sku_response.get('ProductName'),
                                sku_response.get('ComplementName'),
                                sku_response.get('NameComplete'),
                                *s,
                                *sku_response.get('ProductCategories').values(),
                                sku_response.get('BrandName'),
                                *sku_response.get('ProductCategories').values(),
                            ] if text
                        ]
                    )
                    instance_sku.search = search
                    instance_sku.save(update_fields=['search'])
                    images = sku_response.get('Images')
                    for image in images:
                        Image.objects.update_or_create(
                            product=instance_product,
                            sku=instance_sku,
                            image_id=image.get('FileId'),
                            defaults={'name': image.get('ImageName'), 'image_url': image.get('ImageUrl')}
                        )
                    response_price = sku_response.get('price')
                    if response_price:
                        instance_sku_price, _is_new = Price.objects.update_or_create(
                            sku=instance_sku,
                            defaults={
                                'list_price': response_price.get('listPrice'),
                                'cost_price': response_price.get('costPrice'),
                                'markup': response_price.get('markup'),
                                'base_price': response_price.get('basePrice'),
                                'raw_json': {**response_price}
                            }
                        )
                        fixed_prices = response_price.get('fixedPrices')
                        for fixed_price in fixed_prices:
                            FixedPrice.objects.update_or_create(
                                price=instance_sku_price,
                                defaults={
                                    'trade_policy_id': fixed_price.get('tradePolicyId'),
                                    'value': fixed_price.get('value'),
                                    'list_price': fixed_price.get('listPrice'),
                                    'date_range': DateRange.objects.create(
                                        date_time_from=fixed_price.get('dateRange').get('from'),
                                        date_time_to=fixed_price.get('dateRange').get('to'),
                                        raw_json={**fixed_price.get('dateRange')}
                                    ) if fixed_price.get('dateRange') else None,
                                    'min_quantity': fixed_price.get('minQuantity'),
                                    'raw_json': {**fixed_price}
                                }
                            )
                    sku_sellers = sku_response.get('SkuSellers')
                    for sku_seller in sku_sellers:
                        SkuSeller.objects.update_or_create(
                            sku=instance_sku,
                            seller=Seller.objects.filter(store=store, seller_id=sku_seller.get('SellerId')).last(),
                            defaults={
                                'is_active': sku_seller.get('IsActive'),
                                'raw_json': {**sku_seller}
                            }
                        )
            if limit:
                break

    # Delete skus that don't have a product
    Sku.objects.filter(product__store=store).update(search_vector=SearchVector('search'))
    needed()

    return True


def needed():
    Product.objects.filter(name__in=[None, 'None']).delete()
    Sku.objects.filter(product=None).delete()
    # set(map(lambda sku: sku.get_serializer_data, Sku.objects.all()))
