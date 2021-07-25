"""Vtex Api integration."""

# Django
from django.conf import settings

# Models
from chatbot_commerce.stores.models import StoresVtex

# Utilities
import requests
import json


class VtexStores:
    """Wrapper for vtex api service."""

    def _get_all_skus(self, **kwargs):
        """Get all sku's."""
        store = StoresVtex.objects.filter(name='pilatos').get()
        store_name = store.name
        url = f'https://{store_name}.vtexcommercestable.com.br/api/catalog_system/pvt/sku/stockkeepingunitids?page=1&pagesize=100'
        list_id_skus = requests.get(url, headers=store.headers, timeout=1000)
        return list_id_skus

    def _get_unit_sku(self, uri, **kwargs):
        """Get sku specification."""
        store = StoresVtex.objects.filter(name='pilatos').get()
        url = "{}{}".format(settings.URL_SKU, uri)
        id_sku = requests.get(url, headers=store.headers, timeout=1000)
        return id_sku

    def _get_unit_product(self, product_id, **kwargs):
        """Get product unit."""
        store = StoresVtex.objects.filter(name='pilatos').get()
        url = "{}{}".format(settings.URL_PRODUCT, product_id)
        id_product = requests.get(url, headers=store.headers, timeout=1000)
        return id_product

    def _get_product_skus(self, product_id, **kwargs):
        """Get product unit."""
        store = StoresVtex.objects.filter(name='pilatos').get()
        url = "{}/{}".format(settings.URL_PRODUCTS_SKU, product_id)
        products_skus = requests.get(url, headers=store.headers, timeout=1000)
        return products_skus

    # def _get_departments_categories(self):
    #     """Get department and categories."""
    #     store = StoresVtex.objects.filter(name='pilatos').get()
    #     url = "{}/{}".format(settings.URL_DEPARTMENT_CATEGORIES)
    #     departments = requests.get(url, headers=store.headers, timeout=1000)
    #     import ipdb ; ipdb.set_trace()
    #     return departments

    # def _get_json_resource(self, uri, **kwargs):
    #     try:
    #         response_json = {}
    #         method = kwargs.pop('method')
    #         if method == 'get':
    #             response = self._get_unit_sku(uri, **kwargs)
    #         else:
    #             pass
    #         if response.status_code in [requests.codes.ok]:
    #             try:
    #                 response_json = response.json()
    #             except ValueError as e:
    #                 response_json = {
    #                     "status_code": response.status_code,
    #                     "message": e,
    #                 }
    #                 return response_json
    #     except requests.ConnectTimeout as i:
    #         response_json = {
    #             "status_code": 504,
    #             "message": f'TIMEOUT: {str(i)}',
    #         }
    #     except requests.exceptions.RequestException as e:
    #         status_code = getattr(e.response, "status_code", 406)
    #         reason = getattr(e.response, "reason", str(e))
    #         response_json = {
    #             "status_code": status_code,
    #             "message": reason,
    #         }
    #     return response_json

    def total_skus(self, **kwargs):
        return self._get_all_skus().json()

    def unit_sku(self, sku):
        uri = f'stockkeepingunit/{sku}'
        return self._get_unit_sku(uri).json()

    def product_unit(self, product_id):
        uri = f'product/{product_id}'
        return self._get_unit_product(uri).json()

    def products_skus(self, product_id):
        uri = f'stockkeepingunitByProductId/{product_id}'
        return self._get_product_skus(uri).json()
    
    # def departments_categories(self):
    #     return self._get_departments_categories.json()
