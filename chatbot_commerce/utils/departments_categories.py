"""Creation of departments and categories."""

# Models
from chatbot_commerce.products.models import Department, Category, Subcategory, Brand
from chatbot_commerce.stores.models import SaleChannel, Seller

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_sc_sellers(store, task=None):
    vtex = VtexStores(store=store)
    sales_channel = vtex.get_sales_channel()
    if task == 'create':
        db_sc_ids = SaleChannel.objects.filter(store=store).values_list('external_id', flat=True)
    for channel in sales_channel:
        channel_id = channel.get('Id')
        if task == 'create':
            if channel_id in db_sc_ids:
                continue
        if channel_id:
            print(f'store_id: {channel_id}')
            list_sellers = vtex.get_list_sellers_by_sc(sc_id=channel_id)
            sellers = []
            if type(list_sellers) == list:
                for seller in list_sellers:
                    name = seller.get('Name')
                    if name:
                        instance, _ = Seller.objects.update_or_create(
                            store=store, name=name, seller_id=seller.get('SellerId'),
                            defaults={
                                'hibrit_payment_options': seller.get('UseHybridPaymentOptions'),
                                'is_active': seller.get('IsActive'),
                                'description': seller.get('Description'),
                                'raw_json': seller
                            }
                        )
                        sellers.append(instance)
            instance_sale_channel, _ = SaleChannel.objects.update_or_create(
                store=store, external_id=channel_id, name=channel.get('Name'),
                defaults={
                    'is_active': channel.get('IsActive'),
                    'raw_json': channel
                }
            )
            if sellers:
                instance_sale_channel.sellers.add(*sellers)
            else:
                print(f'no sellers: {sellers}')
        else:
            print(f'error: channel: {channel}, sales_channel: {sales_channel}')
        if channel_id == 1:
            break


def get_departments(store):
    """Creation departments and categories."""
    vtex = VtexStores(store=store)
    departments = vtex.departments_categories()
    for department in departments:
        children = department['children']
        departament_obj, _ = Department.objects.update_or_create(
            external_id=department.get('id'),
            store=store,
            defaults={
                'name': department.get('name'),
                'title': department.get('Title'),
                'description': department.get('MetaTagDescription'),
                'raw_json': department,
            }
        )
        for category in children:
            category_obj, _ = Category.objects.update_or_create(
                external_id=category.get('id'),
                department=departament_obj,
                defaults={
                    'name': category.get('name'),
                    'title': category.get('Title'),
                    'description': category.get('MetaTagDescription'),
                    'raw_json': category,
                }
            )
            sub_categories = category.get('children')
            if sub_categories:
                for item in sub_categories:
                    Subcategory.objects.get_or_create(
                        external_id=item.get('id'),
                        category=category_obj,
                        defaults={
                            'name': item.get('name'),
                            'title': item.get('Title'),
                            'description': item.get('MetaTagDescription'),
                            'raw_json': item,
                        }
                    )


def get_brands(store):
    """Creation departments and categories."""
    vtex = VtexStores(store=store)
    brands = vtex.get_brands()
    for brand in brands:
        Brand.objects.update_or_create(
            store=store,
            external_id=brand.get('id'),
            defaults={
                'name': brand.get('name'),
                'title': brand.get('Title'),
                'description': brand.get('MetaTagDescription'),
                'raw_json': brand,
            }
        )
