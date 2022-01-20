"""Shopify Api integration."""

# Utilities
import requests
import urllib3
import json


class ShopifyStores:
    """Wrapper for shopify api service."""

    def __init__(self, store):
        self.store = store
        # self.vtexprice = VtexPriceSku(store=store)
        self.http = urllib3.HTTPSConnectionPool(headers=store.headers, host=f'{store.name}.{store.url_enviroment}')

    def _get_resources(self, uri, **kwargs):
        """Get resources for store."""
        url = "{}/{}".format(self.store.urls['base_url'], uri)
        print(url)
        lr = list()
        while 1:
            r = self.http.request(method='GET', url=url)
            try:
                if r.status in [requests.codes.ok]:
                    response_json = list(json.loads(r.data.decode('utf-8')).values())[0]
                    lr += response_json
            except ValueError as e:
                response_json = {
                    "status_code": r.status,
                    "message": e,
                }
                break
            link = r.headers.get('Link')
            if link and 'rel="next"' in link:
                link = link.split(',')[-1].strip()
                url = link[1:link.find('>')]
            else:
                break
        return lr

    def _get_json_resource(self, uri, **kwargs):
        try:
            method = kwargs.pop('method')
            if method == 'get':
                response_json = self._get_resources(uri, **kwargs)
            else:
                pass
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

    def collections(self, query_params, **kwargs):
        uri = 'collection_listings.json'
        if query_params:
            uri = '?'.join((uri, query_params,))
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def products(self, query_params, **kwargs):
        uri = 'products.json'
        if query_params:
            uri = '?'.join((uri, query_params,))
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def product_listings(self, query_params, **kwargs):
        uri = 'product_listings.json'
        if query_params:
            uri = '?'.join((uri, query_params,))
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )
