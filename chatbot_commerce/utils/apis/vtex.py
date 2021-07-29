"""Vtex Api integration."""

# Django
from django.conf import settings

# Models
from chatbot_commerce.stores.models import StoresVtex

# Utilities
import requests


class VtexStores:
    """Wrapper for vtex api service."""

    def _get_resources(self, uri, **kwargs):
        """Get resources for store."""
        store = StoresVtex.objects.filter(name='pilatos').get()
        url = "{}/{}".format(settings.URL_VTEX, uri)
        r = requests.get(url, headers=store.headers, timeout=1000)
        return r

    def _get_json_resource(self, uri, **kwargs):
        try:
            response_json = {}
            method = kwargs.pop('method')
            if method == 'get':
                response = self._get_resources(uri, **kwargs)
            else:
                pass
            if response.status_code in [requests.codes.ok]:
                try:
                    response_json = response.json()
                except ValueError as e:
                    response_json = {
                        "status_code": response.status_code,
                        "message": e,
                    }
                    return response_json
        except requests.ConnectTimeout as i:
            response_json = {
                "status_code": 504,
                "message": f'TIMEOUT: {str(i)}',
            }
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, "status_code", 406)
            reason = getattr(e.response, "reason", str(e))
            response_json = {
                "status_code": status_code,
                "message": reason,
            }
        return response_json

    def total_skus(self, **kwargs):
        uri = 'catalog_system/pvt/sku/stockkeepingunitids?page=1&pagesize=100'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def unit_sku(self, sku):
        uri = f'catalog/pvt/stockkeepingunit/{sku}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def product_unit(self, product_id):
        uri = f'catalog/pvt/product/{product_id}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def products_skus(self, product_id):
        uri = f'catalog_system/pvt/sku/stockkeepingunitByProductId/{product_id}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def image_sku(self, sku_id):
        uri = f'catalog/pvt/stockkeepingunit/{sku_id}/file'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def departments_categories(self):
        uri = 'catalog_system/pub/category/tree/10'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )


class VtexPriceSku:

    def _get_resource(self, uri, **kwargs):
        store = StoresVtex.objects.filter(name='pilatos').get()
        url = '{}/{}'.format(settings.URL_PRICESKU_VTEX, uri)
        r = requests.get(url, headers=store.headers, timeout=1000)
        return r

    def _get_json_resource(self, uri, **kwargs):
        try:
            response_json = {}
            method = kwargs.pop('method')
            if method == 'get':
                response = self._get_resource(uri, **kwargs)
            else:
                pass
            if response.status_code in [requests.codes.ok]:
                try:
                    response_json = response.json()
                except ValueError as e:
                    response_json = {
                        "status_code": response.status_code,
                        "message": e
                    }
                    return response_json
        except requests.ConnectionError as i:
            response_json = {
                "status_code": 504,
                "message": f"TIMEOUT: {str(i)}"
            }
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, "status_code", 406)
            reason = getattr(e.response, "resaon", str(e))
            response_json = {
                "status_code": status_code,
                "message": reason
            }
        return response_json

    def price_sku(self, sku_id):
        uri = f'pricing/prices/{sku_id}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )
