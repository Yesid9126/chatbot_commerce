"""Creation of departments and categories."""

# Models
from chatbot_commerce.stores.models import (
    Department,
    Category,
    Subcategory,
    Brand,
    SaleChannel,
    Seller,
)

# Apis
from chatbot_commerce.utils.apis import VtexStores, ShopifyStores


def get_sc_sellers(store, task=None):
    if store.store_type.name == "VTEX":
        vtex = VtexStores(store=store)
        sales_channel = vtex.get_sales_channel()
        if task == "create":
            db_sc_ids = SaleChannel.objects.filter(store=store).values_list(
                "external_id", flat=True
            )
        for channel in sales_channel:
            channel_id = channel.get("Id")
            if task == "create":
                if channel_id in db_sc_ids:
                    continue
            if channel_id:
                print(f"store_id: {channel_id}")
                list_sellers = vtex.get_list_sellers_by_sc(sc_id=channel_id)
                sellers = []
                if type(list_sellers) is list:
                    for seller in list_sellers:
                        name = seller.get("Name")
                        if name:
                            instance, _ = Seller.objects.update_or_create(
                                store=store,
                                name=name,
                                seller_id=seller.get("SellerId"),
                                defaults={
                                    "hibrit_payment_options": seller.get(
                                        "UseHybridPaymentOptions"
                                    ),
                                    "is_active": seller.get("IsActive"),
                                    "description": seller.get("Description"),
                                    "raw_json": seller,
                                },
                            )
                            sellers.append(instance)
                instance_sale_channel, _ = SaleChannel.objects.update_or_create(
                    store=store,
                    external_id=channel_id,
                    name=channel.get("Name"),
                    defaults={
                        "is_active": channel.get("IsActive"),
                        "raw_json": channel,
                    },
                )
                if sellers:
                    instance_sale_channel.sellers.add(*sellers)
                else:
                    print(f"no sellers: {sellers}")
            else:
                print(f"error: channel: {channel}, sales_channel: {sales_channel}")
            if channel_id == 1 or channel_id == "1":
                sales_channel.clear()
        sales_channel.clear()


def get_departments(store):
    """Creation departments and categories."""
    if store.store_type.name == "VTEX":
        vtex = VtexStores(store=store)
        departments = vtex.departments_categories()
        for department in departments:
            department_obj, _ = Department.objects.get_or_create(
                name=department.get("name").strip().capitalize(),
            )
            e_id = department.get("id")
            e_id = "".join(
                (
                    store.store_type.name,
                    store.name,
                    str(e_id),
                )
            )
            if e_id not in department_obj.external_id:
                department_obj.external_id.append(e_id)
                department_obj.save()
            department_obj.stores.add(store)

            children = department["children"]
            for category in children:
                category_obj, _ = Category.objects.update_or_create(
                    external_id=category.get("id"),
                    store=store,
                    department=department_obj,
                    defaults={"name": category.get("name")},
                )

                sub_categories = category.get("children")
                if sub_categories:
                    for subcategory in sub_categories:
                        subcategory_obj, _ = Subcategory.objects.update_or_create(
                            external_id=subcategory.get("id"),
                            category=category_obj,
                            defaults={"name": subcategory.get("name")},
                        )

    elif store.store_type.name == "SHOPIFY":
        shopify = ShopifyStores(store=store)
        product_array = shopify.products(query_params="limit=250&fields=product_type")
        departments = {
            product_dict.get("product_type") for product_dict in product_array
        }
        departments = {
            Department.objects.get_or_create(
                name=department.strip().capitalize(),
            )
            for department in departments
        }
        {department[0].stores.add(store) for department in departments}

    departments.clear()


def get_brands(store):
    """Creation departments and categories."""
    if store.store_type.name == "VTEX":
        vtex = VtexStores(store=store)
        brands = vtex.get_brands()
        for brand in brands:
            brand_obj, _ = Brand.objects.get_or_create(
                name=brand.get("name").strip().capitalize(),
            )
            e_id = brand.get("id")
            e_id = "".join(
                (
                    store.store_type.name,
                    store.name,
                    str(e_id),
                )
            )
            if e_id not in brand_obj.external_id:
                brand_obj.external_id.append(e_id)
                brand_obj.save()
            brand_obj.stores.add(store)

    elif store.store_type.name == "SHOPIFY":
        shopify = ShopifyStores(store=store)
        product_array = shopify.products(query_params="limit=250&fields=vendor")
        brands = {product_dict.get("vendor") for product_dict in product_array}

        brands = {
            Brand.objects.get_or_create(
                name=brand.strip().capitalize(),
            )
            for brand in brands
        }
        {brand[0].stores.add(store) for brand in brands}

    brands.clear()
