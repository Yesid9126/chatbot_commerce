"""Vtex Api integration."""

# Django
from django.conf import settings

# Utilities
# from chatbot_commerce.stores.models import StoresVtex
import urllib
import requests
import json


class VtexStores:
    """Wrapper for vtex api service."""


    def _get_resource(self, uri, **kwargs):
        """Get resource method."""
        # querystring = urllib.parse.urlencode(kwargs)
        # url = "{}/{}?{}".format(settings.URL_VTEX_STORES, uri, querystring)
        url = f'https://pilatos.vtexcommercestable.com.br/api/catalog_system/pvt/sku/stockkeepingunitids?page=1&pagesize=100'
        headers = {
            'X_VTEX_API_AppKey': settings.X_VTEX_API_AppKey,
            'X_VTEX_API_AppToken': settings.X_VTEX_API_AppToken,
        }
        list_id_sku = requests.get(url, headers=headers, timeout=1000)
        return list_id_sku

    def _get_resource_sku(self, uri, **kwargs):
        """Get resource method."""
        url = "{}".format(settings.URL_VTEX_STORES, uri)
        headers = {
            'X_VTEX_API_AppKey': settings.X_VTEX_API_AppKey,
            'X_VTEX_API_AppToken': settings.X_VTEX_API_AppToken,
        }
        id_sku = requests.get(url, headers=headers, timeout=1000)
        return id_sku
    
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

    def total_skus(self):
        # uri = 'sku'
        method = 'get'
        return self._get_json_resource(
            # uri,
            method=method
        )

    def unit_sku(self):
        uri ='stockkeepingunit/'
        method = 'get'
        return self._get_json_resource(
            uri,
            method=method
        )
