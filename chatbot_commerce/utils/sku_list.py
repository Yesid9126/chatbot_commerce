"""Store sku list"""

# Django Rest Framework
from rest_framework import status

# Models
from chatbot_commerce.products.models import Skus

# Apis
from chatbot_commerce.utils.apis.vtex import VtexStores


def get_sku_vtex_store():
    """Get all sku's available in shop."""
    vtex = VtexStores()
    skus = vtex.total_skus()
    skus_ids = []
    if skus:
        for sku in skus_ids:
            vtex.unit_sku(sku)
