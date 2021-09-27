"""Construction of payment url."""

# Django
from rest_framework.response import Response


def cart_url(self, list_sku):
    sku = list_sku
    import ipdb; ipdb.set_trace()