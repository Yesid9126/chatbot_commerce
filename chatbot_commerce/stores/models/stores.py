"""Stores model."""

# Django
from django.db import models

# utilities
from chatbot_commerce.utils.models import ChatbootModel
# from chatbot_commerce.products.models.products import Product

class StoresVtex(ChatbootModel):
    """Stores model."""

    name = models.CharField(
        max_length=255,
    )

    url_enviroment = models.CharField(
        max_length=500
    )

    appi_key = models.CharField(
        max_length=500
    )

    api_token = models.CharField(
        max_length=500
    )

    def __str__(self):
        """Return store name."""
        return f'sku:{self.sku_id}'

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"
    
    @property
    def headers(self):
        headers = {
            "X-VTEX-API-AppKey": f"{self.appi_key}",
            "X-VTEX-API-AppToken": f"{self.api_token}"
        }
        return headers

    @property
    def urls(self):
        core_url = f"https://{self.name}.{self.url_enviroment}.com.br/api"
        core_uri_1 = f"{core_url}/catalog/pvt" 
        core_uri_2 = f"{core_url}/catalog_system/pvt"
        urls = {
            "product": {
                "productID": {
                    "onlyProduct" : f"{core_uri_1}/product",
                    "product&context": f"{core_uri_2}/products/ProductGet",
                    "product&tradePolicy": f"{core_uri_2}/products/productget"
                },
                "productRefId": {
                    "onlyProduct": f"{core_uri_2}/products/productgetbyrefid",
                }
            },
            "category": {
                "categoryID": {
                    "onlyCategory": f"{core_uri_1}/category"
                }
            }
        }
        return urls
