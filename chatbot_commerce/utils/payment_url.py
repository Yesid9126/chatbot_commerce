"""Construction of payment url."""

# Django
from rest_framework.response import Response

# Models
from chatbot_commerce.stores.models import Store, SkuSeller


def kart_url(store, list_sku):
    skus = list_sku
    url = 'https://www.pilatos.com/checkout/cart/add?sc=1&sku=7686+7690&qty=1&seller=1'
    stores = Store.objects.filter(name=store).get()
    for sku in skus:
        sku_id = sku['sku_id']
        quantity = sku['quantity']
        seller = SkuSeller.objects.filter(sku__external_id=sku_id).get()
        import ipdb; ipdb.set_trace()
        cadena = f'sc=1&sku='
    