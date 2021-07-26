"""Creation of departments and categories."""

# Models
from chatbot_commerce.products.models import StoreDepartment, CategoriesStore

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores

def get_departments():
    """Creation departments and categories."""
    vtex = VtexStores()
    departments = vtex.departments_categories()
    for department in departments:
        children = department.pop('children')
        departamento, created = StoreDepartment.objects.update_or_create(
            defaults={
                'department_id': department.get('id'),
                'department_name': department.get('name'),
                'url_department': department.get('url'),
                'has_children': department.get('hasChildren'),
                'title': department.get('Title'),
                'tag_description': department.get('MetaTagDescription'),
                'department_json': department,
            })