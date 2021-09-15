"""Vtex Api integration."""

# Utilities
import requests


class VtexStores:
    """Wrapper for vtex api service."""

    def __init__(self, store):
        self.store = store

    def _get_resources(self, uri, **kwargs):
        """Get resources for store."""
        url = "{}/{}".format(self.store.urls['base_url'], uri)
        r = requests.get(url, headers=self.store.headers, timeout=1000)
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

    def total_skus(self, page, **kwargs):
        # TODO: Pagination as args for big stores
        uri = f'catalog_system/pvt/sku/stockkeepingunitids?page={page}&pagesize=1000'
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
        uri = f'catalog_system/pvt/products/productget/{product_id}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def product_skus(self, product_id):
        uri = f'catalog_system/pvt/sku/stockkeepingunitByProductId/{product_id}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def skus_inventory(self, sku_id):
        uri = f'logistics/pvt/inventory/skus/{sku_id}'
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
        uri = 'catalog_system/pub/category/tree/20'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def get_brands(self):
        uri = 'catalog_system/pvt/brand/list'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def get_sku_specifications(self, sku_id):
        uri = f'catalog/pvt/stockkeepingunit/{sku_id}/specification'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def get_specifications_field(self, field_id):
        uri = f'catalog_system/pub/specification/fieldGet/{field_id}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def get_sales_channel(self):
        uri = 'catalog_system/pvt/saleschannel/list'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def get_list_skus_by_storeid(self, store_id):
        uri = f'catalog_system/pvt/sku/stockkeepingunitidsbysaleschannel?sc={store_id}&page=1&pageSize=1999999999'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )


class VtexPriceSku:

    def __init__(self, store):
        self.store = store

    def _get_resource(self, uri, **kwargs):
        url = '{}/{}'.format(self.store.urls['base_price_url'], uri)
        r = requests.get(url, headers=self.store.headers, timeout=1000)
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
