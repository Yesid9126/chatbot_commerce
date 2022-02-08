"""Vtex Api integration."""

# Utilities
import requests
import urllib3
import json

import asyncio
from aiohttp import ClientSession


class VtexApi:
    """Wrapper for vtex api service."""
    def __init__(self, store):
        self.store = store
        self.sem = asyncio.Semaphore(1000)
        self.headers = store.headers | {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    async def _get_resources(self, uri, session, **kwargs):
        try:
            async with session.get("{}/{}".format(self.base_url, uri)) as response:
                return await response.json()
        except Exception as e:
            print(e)
        return dict()

    async def _bound_get_resources(self, uri, session, **kwargs):
        async with self.sem:
            return await self._get_resources(uri, session, **kwargs)

    async def get_products(self, product_ids, **kwargs):
        """Get products from vtex."""

        self.base_url = self.store.urls['base_url']
        uri = 'catalog_system/pvt/products/productget/{}'
        async with ClientSession(headers=self.headers) as session:
            tasks = [asyncio.ensure_future(self._bound_get_resources(uri.format(product_id), session, **kwargs)) for product_id in product_ids]
            responses = asyncio.gather(*tasks)
            return await responses

    async def get_skus(self, sku_ids, **kwargs):
        """Get products from vtex."""

        self.base_url = self.store.urls['base_url']
        uri = 'catalog_system/pvt/sku/stockkeepingunitbyid/{}'
        async with ClientSession(headers=self.headers) as session:
            tasks = [asyncio.ensure_future(self._bound_get_resources(uri.format(sku_id), session, **kwargs)) for sku_id in sku_ids]
            responses = asyncio.gather(*tasks)
            return await responses

    async def get_sku_prices(self, sku_ids, **kwargs):
        """Get products from vtex."""

        self.base_url = self.store.urls['base_price_url']
        uri = 'pricing/prices/{}'
        async with ClientSession(headers=self.headers) as session:
            tasks = [asyncio.ensure_future(self._bound_get_resources(uri.format(sku_id), session, **kwargs)) for sku_id in sku_ids]
            responses = asyncio.gather(*tasks)
            return await responses

    async def get_sku_inventories(self, product_ids, **kwargs):
        """Get products from vtex."""

        self.base_url = self.store.urls['base_url']
        uri = 'logistics/pvt/inventory/skus/{}'
        async with ClientSession(headers=self.headers) as session:
            tasks = [asyncio.ensure_future(self._bound_get_resources(uri.format(product_id), session, **kwargs)) for product_id in product_ids]
            responses = asyncio.gather(*tasks)
            return await responses
class VtexStores:
    """Wrapper for vtex api service."""

    def __init__(self, store):
        self.store = store
        self.vtexprice = VtexPriceSku(store=store)
        self.http = urllib3.HTTPSConnectionPool(headers=store.headers, host=f'{store.name}.{store.url_enviroment}')

    def _get_resources(self, uri, **kwargs):
        """Get resources for store."""
        url = "{}/{}".format(self.store.urls['base_url'], uri)
        r = self.http.request(method='GET', url=url)
        return r

    def _get_json_resource(self, uri, **kwargs):
        try:
            response_json = {}
            method = kwargs.pop('method')
            if method == 'get':
                response = self._get_resources(uri, **kwargs)
            else:
                pass
            if response.status in [requests.codes.ok]:
                try:
                    response_json = json.loads(response.data.decode('utf-8'))
                except ValueError as e:
                    response_json = {
                        "status_code": response.status,
                        "message": e,
                    }
                    return response_json
        except urllib3.exceptions.ConnectTimeoutError as i:
            response_json = {
                "status_code": 504,
                "message": f'TIMEOUT: {str(i)}',
            }
        except urllib3.exceptions.RequestError as e:
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
        uri = f'catalog_system/pvt/products/ProductGet/{product_id}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def get_product_ids_with_sku_ids(self, from_position, to_position):
        uri = f'catalog_system/pvt/products/GetProductAndSkuIds?_from={from_position}&_to={to_position}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )


    def get_sku_context(self, sku_id):
        # Quantity in warehouses
        total_quantity = 0
        price_dic = False
        if sku_id:
            sku_inventory = self.skus_inventory(sku_id=sku_id)
            sku_price = self.vtexprice.price_sku(sku_id=sku_id)
            listprice = sku_price.get('listPrice')
            if listprice:
                price_dic = sku_price
            sku_inventory = sku_inventory.get('balance')
            if sku_inventory:
                for quantity in sku_inventory:
                    quantity_sku = quantity.get('totalQuantity')
                    total_quantity += quantity_sku
        else:
            print(f'error in sku: {sku_id} line 164 utils/products.py')

        uri = f'catalog_system/pvt/sku/stockkeepingunitbyid/{sku_id}'
        method = 'get'

        return self._get_json_resource(
            uri,
            method=method
        ) | {'total_quantity': total_quantity, 'price': price_dic}

    def skus_inventory(self, sku_id):
        uri = f'logistics/pvt/inventory/skus/{sku_id}'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def product_skus(self, product_id):
        uri = f'catalog_system/pub/products/variations/{product_id}'
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

    def get_list_skus_by_storeid(self, store_id, page):
        uri = f'catalog_system/pvt/sku/stockkeepingunitidsbysaleschannel?sc={store_id}&page={page}&pageSize=1999999999'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def get_list_sellers_by_sc(self, sc_id):
        uri = f'catalog_system/pvt/seller/list?sc={sc_id}&sellerType=1&isBetterScope=false'
        method = 'get'
        r1 = self._get_json_resource(
            uri,
            method=method
        )
        uri = f'catalog_system/pvt/seller/list?sc={sc_id}&sellerType=1&isBetterScope=true'
        r2 = self._get_json_resource(
            uri,
            method=method
        )
        print(f'r1: {r1}, r2: {r2}')
        if type(r2) == type(r1) == list:
            return r2 + r1
        if type(r2) == list:
            return r2
        if type(r1) == list:
            return r1
        return [r1, r2]


class VtexPriceSku:

    def __init__(self, store):
        self.store = store
        self.http = urllib3.HTTPSConnectionPool(headers=self.store.headers, host='api.vtex.com')

    def _get_resource(self, uri, **kwargs):
        url = '{}/{}'.format(self.store.urls['base_price_url'], uri)
        r = self.http.request(method='GET', url=url)
        return r

    def _get_json_resource(self, uri, **kwargs):
        try:
            response_json = {}
            method = kwargs.pop('method')
            if method == 'get':
                response = self._get_resource(uri, **kwargs)
            else:
                pass
            if response.status in [requests.codes.ok]:
                try:
                    response_json = json.loads(response.data.decode('utf-8'))
                except ValueError as e:
                    response_json = {
                        "status_code": response.status,
                        "message": e
                    }
                    return response_json
        except urllib3.exceptions.ConnectTimeoutError as i:
            response_json = {
                "status_code": 504,
                "message": f"TIMEOUT: {str(i)}"
            }
        except urllib3.exceptions.RequestError as e:
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
