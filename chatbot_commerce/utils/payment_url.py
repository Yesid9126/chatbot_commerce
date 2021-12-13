"""Construction of payment url."""

# Models
from chatbot_commerce.stores.models import Sku, Store


def kart_url(store, list_sku):
    skus = list_sku
    stores = Store.objects.filter(name=store).get()
    url = stores.domain
    cadena = []
    for sku in skus:
        sku_id = sku['sku_id']
        quantity = sku['quantity']
        sku_seller = Sku.objects.get(external_id=sku_id)
        seller = int(sku_seller.serializer_data.get('seller_id'))
        cadena.append(f'sc=1&sku={sku_id}&qty={quantity}&seller={seller}')
    cadena = '&'.join(cadena)
    url = ''.join([url, cadena])
    return url
