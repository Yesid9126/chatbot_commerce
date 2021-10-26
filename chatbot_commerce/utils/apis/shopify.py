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
        lr = []
        while 1:
            r = self.http.request(method='GET', url=url)
            link = r.headers.get('Link').split(',')[-1].strip()
            if 'rel="next"' in link:
                url = link[1:link.find('>')]
            else:
                break
            lr.append(r)
        return lr

    def _get_json_resource(self, uri, **kwargs):
        try:
            response_json = {}
            method = kwargs.pop('method')
            if method == 'get':
                list_response = self._get_resources(uri, **kwargs)
            else:
                pass
            response_json = []
            for response in list_response:
                if response.status in [requests.codes.ok]:
                    try:
                        response_json += json.loads(response.data.decode('utf-8'))
                    except ValueError as e:
                        response_json = {
                            "status_code": response.status,
                            "message": e,
                        }
                        break
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

    def collections(self, **kwargs):
        uri = f'collection_listings.json?limit=250'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )

    def products(self, **kwargs):
        uri = f'product_listings.json?limit=100'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )
