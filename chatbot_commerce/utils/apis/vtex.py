"""Vtex Api integration."""

# Django
from django.conf import settings

# Utilities
import urllib
import requests
import json


class Vtex:
    """Wrapper for vtex api service."""


    def _get_resource(self, uri, **kwargs):
        """Get resource method."""
        querystring = urllib.parse.urlencode(kwargs)
        url = "{}/{}?{}".format(settings.URL_VTEX_API, uri, querystring)
        headers = {
            'X-VTEX-API-AppKey': settings.API_PASSWORD,
            'X-VTEX-API-AppToken': settings.API_KEY,
            "Accept": "application/json",
            'Content-Type': 'application/json'
        }
        r = requests.get(url, headers=headers, timeout=10)
        return r


    def _get_json_resource(self, uri, **kwargs):
        try:
            response_json = {}
            method = kwargs.pop('method')
            if method == 'get':
                response = self._get_resource(uri, **kwargs)
            else:
                response = self._post_resource(uri, **kwargs)
            response.raise_for_status()
            if response.status_code in [requests.codes.ok, requests.codes.created]:
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