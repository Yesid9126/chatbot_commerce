"""Construction of payment url."""

# Models
from chatbot_commerce.stores.models import Store
from chatbot_commerce.products.models import Skus


def kart_url(store, list_sku):
    skus = list_sku
    url = 'https://www.pilatos.com/checkout/cart/add?sc=1&sku=7686+7690&qty=1&seller=1'
    stores = Store.objects.filter(name=store).get()
    url = stores.domain
    cadena = []
    for sku in skus:
        sku_id = sku['sku_id']
        quantity = sku['quantity']
        sku_seller = Skus.objects.get(external_id=sku_id)
        seller = int(sku_seller.serializer_data.get('seller_id'))
        cadena.append(f'sc=1&sku={sku_id}&qty={quantity}&seller={seller}')
    cadena = '&'.join(cadena)
    url = ''.join([url, cadena])
    return url
