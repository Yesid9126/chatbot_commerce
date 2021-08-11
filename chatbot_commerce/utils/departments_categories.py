"""Creation of departments and categories."""

# Models
from chatbot_commerce.products.models import Department, Category, Subcategory, Brand
from chatbot_commerce.stores.models import Store

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_departments(store):
    """Creation departments and categories."""
    vtex = VtexStores()
    departments = vtex.departments_categories()
    store = Store.objects.last()
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


def get_brands():
    """Creation departments and categories."""
    vtex = VtexStores()
    brands = vtex.get_brands()
    for brand in brands:
        Brand.objects.update_or_create(
            external_id=brand.get('id'),
            defaults={
                'name': brand.get('name'),
                'title': brand.get('Title'),
                'description': brand.get('MetaTagDescription'),
                'raw_json': brand,
            }
        )
