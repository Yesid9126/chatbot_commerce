"""Creation of departments and categories."""

# Models
from chatbot_commerce.products.models import Department, Category

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_departments(store):
    """Creation departments and categories."""
    vtex = VtexStores()
    departments = vtex.departments_categories()
    for department in departments:
        children = department['children']
        departament, created = Department.objects.update_or_create(
            department_id=department.get('id'),
            store=store,
            defaults={
                'department_name': department.get('name'),
                'url_department': department.get('url'),
                'has_children': department.get('hasChildren'),
                'title': department.get('Title'),
                'tag_description': department.get('MetaTagDescription'),
                'department_json': department,
            }
        )
        for category in children:
            categories, created = Category.objects.update_or_create(
                category_id=category.get('id'),
                defaults={
                    'category_name': category.get('name'),
                    'has_children': category.get('hasChildren'),
                    'departments': departament,
                    'categories_json': category
                }
            )
            if category.get('children'):
                pass
