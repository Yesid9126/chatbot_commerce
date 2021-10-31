"""Creation of departments and categories."""

# Models
from chatbot_commerce.stores.models import Department, Category, Subcategory, Brand, SaleChannel, Seller

# Apis
from chatbot_commerce.utils.apis import VtexStores, ShopifyStores


def get_sc_sellers(store, task=None):
    if store.store_type.name == 'VTEX':
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
            if channel_id == 1 or channel_id == '1':
                sales_channel.clear()
                break
        sales_channel.clear()


def get_departments(store):
    """Creation departments and categories."""
    if store.store_type.name == 'VTEX':
        vtex = VtexStores(store=store)
        departments = vtex.departments_categories()
        for department in departments:
            children = department['children']
            departament_obj, _ = Department.objects.get_or_create(
                name=department.get('name'),
            )
            e_id = department.get("Id")
            e_id = "".join((store.store_type.name, store.name, str(e_id),))
            if e_id not in departament_obj.external_id:
                departament_obj.external_id.append(e_id)
                departament_obj.save()
            departament_obj.stores.add(store)
            for category in children:
                category_obj, _ = Category.objects.get_or_create(
                    name=category.get('name'),
                )
                e_id = category.get("Id")
                e_id = "".join((store.store_type.name, store.name, str(e_id),))
                if e_id not in category_obj.external_id:
                    category_obj.external_id.append(e_id)
                    category_obj.save()
                category_obj.stores.add(store)
                departament_obj.categories.add(category_obj)
                sub_categories = category.get('children')
                if sub_categories:
                    for subcategory in sub_categories:
                        subcategory_obj, _ = Subcategory.objects.get_or_create(
                            name=subcategory.get('name'),
                        )
                        e_id = subcategory.get("Id")
                        e_id = "".join((store.store_type.name, store.name, str(e_id),))
                        if e_id not in subcategory_obj.external_id:
                            subcategory_obj.external_id.append(e_id)
                            subcategory_obj.save()
                        subcategory_obj.stores.add(store)
                        category_obj.subcategories.add(subcategory_obj)
    elif store.store_type.name == 'SHOPIFY':
        shopify = ShopifyStores(store=store)
        product_array = shopify.products(query_params='limit=250&fields=product_type')
        departments = {department_dict.get('product_type').strip().capitalize() for product_dict in product_array for department_dict in product_dict.get('products')}
        departments = {
            Department.objects.get_or_create(
                name=department,
            )
            for department in departments
        }
        {department[0].stores.add(store) for department in departments}

    departments.clear()


def get_brands(store):
    """Creation departments and categories."""
    if store.store_type.name == 'VTEX':
        vtex = VtexStores(store=store)
        brands = vtex.get_brands()
        for brand in brands:
            brand_obj, _ = Brand.objects.get_or_create(
                name=brand.get('name').strip().capitalize(),
            )
            e_id = brand.get("id")
            e_id = "".join((store.store_type.name, store.name, str(e_id),))
            if e_id not in brand_obj.external_id:
                brand_obj.external_id.append(e_id)
                brand_obj.save()
            brand_obj.stores.add(store)

    elif store.store_type.name == 'SHOPIFY':
        shopify = ShopifyStores(store=store)
        product_array = shopify.products(query_params='limit=250&fields=vendor')
        brands = {vendor_dict.get('vendor').strip().capitalize() for product_dict in product_array for vendor_dict in product_dict.get('products')}

        brands = {
            Brand.objects.get_or_create(
                name=brand.strip().capitalize(),
            )
            for brand in brands
        }
        {brand[0].stores.add(store)for brand in brands}

    brands.clear()
