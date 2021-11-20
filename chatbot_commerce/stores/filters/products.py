# Django
from django_filters.rest_framework import FilterSet
from django_filters import filters

# Models
from chatbot_commerce.stores.models import Product, Skus, Image
from django.db.models import Q, Prefetch

# Utils
from random import shuffle
from django.core.cache import cache
# from db_python import query_debugger


class ProductFilterSet(FilterSet):

    # attributes = filters.CharFilter(field_name='name')
    stock_quantity = filters.CharFilter(field_name='name')
    offset = filters.CharFilter(field_name='name')
    limit = filters.CharFilter(field_name='name')
    page = filters.CharFilter(field_name='name')

    class Meta:
        model = Product
        fields = [
            'offset',
            'limit',
            'search',
            'page',
            #  'attributes',
            'stock_quantity',
        ]


def products_skus(self, store_pk):
    """
    Plane function of apply_filters of model Store.
    """
    product_d = dict()
    # Apply filter products
    if self.store.apply_filter_enable_products and self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:
        sku_q = [~Q(images=None), ~Q(price=None)]
        sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'total_quantity__gt': 0, 'is_active': True, 'product__store': store_pk}
        product_d['is_active'] = True

    elif self.store.apply_filter_enable_products or self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_products:
            if self.store.apply_filter_enable_skus:
                if self.store.apply_filter_image:
                    sku_q = [~Q(images=None)]
                    sku_d = self.skus_filter_data | {'total_quantity__gt': 0, 'is_active': True, 'product__store': store_pk}
                elif self.store.apply_filter_price:
                    sku_q = [~Q(price=None)]
                    sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'total_quantity__gt': 0, 'is_active': True, 'product__store': store_pk}
                else:
                    sku_q = list()
                    sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'total_quantity__gt': 0, 'is_active': True, 'product__store': store_pk}
            elif self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    sku_q = [~Q(images=None), ~Q(price=None)]
                    sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'product__store': store_pk}
                else:
                    sku_q = [~Q(images=None)]
                    sku_d = self.skus_filter_data | {'product__store': store_pk}
            elif self.store.apply_filter_price:
                sku_q = [~Q(price=None)]
                sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'product__store': store_pk}
            else:
                sku_q = list()
                sku_d = self.skus_filter_data | {'product__store': store_pk}
            product_d['is_active'] = True

        elif self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    sku_q = [~Q(images=None), ~Q(price=None)]
                    sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'total_quantity__gt': 0, 'is_active': True, 'product__store': store_pk}
                else:
                    sku_q = [~Q(images=None)]
                    sku_d = self.skus_filter_data | {'total_quantity__gt': 0, 'is_active': True, 'product__store': store_pk}
            elif self.store.apply_filter_price:
                sku_q = [~Q(price=None)]
                sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'total_quantity__gt': 0, 'is_active': True, 'product__store': store_pk}
            else:
                sku_q = list()
                sku_d = self.skus_filter_data | {'total_quantity__gt': 0, 'is_active': True, 'product__store': store_pk}

        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:
                sku_q = [~Q(images=None), ~Q(price=None)]
                sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'product__store': store_pk}
            else:
                sku_q = [~Q(images=None)]
                sku_d = self.skus_filter_data | {'product__store': store_pk}

        else:
            sku_q = [~Q(price=None)]
            sku_d = self.skus_filter_data | {'price__base_price__gt': 0, 'product__store': store_pk}

    else:
        sku_q = list()
        sku_d = self.skus_filter_data | {'product__store': store_pk}

    skus_pk = Skus.objects\
        .filter(*sku_q, **sku_d)\
        .values_list('pk', flat=True)
    data = cache.get(key=self.search)
    if data:
        count = data.get('count')
        products_external_id = data.get('products_external_id')

    else:
        product_is_active = product_d.get('is_active')
        if product_is_active:
            products_external_id = list(set(Product.objects.filter(skus__in=skus_pk, is_active=True).values_list('external_id', flat=True)))
        else:
            products_external_id = list(set(Product.objects.filter(skus__in=skus_pk).values_list('external_id', flat=True)))
        # products_external_id = sorted(products_external_id)
        shuffle(products_external_id)
        # products_external_id.reverse()
        count = len(products_external_id)
        data = {
            'products_external_id': products_external_id,
            'count': count
        }
        cache.set(key=self.search, value=data, timeout=60 * 15)
    products_external_id = products_external_id[self.offset:self.limit]
    queryset = Product.objects.only('external_id', 'name', 'keywords', 'department', 'category', 'sub_category', 'brand')\
        .select_related('department', 'category', 'sub_category', 'brand')\
        .prefetch_related(
            Prefetch(
                'skus',
                queryset=Skus.objects.only('serializer_data', 'product').filter(pk__in=skus_pk, product__external_id__in=products_external_id),
                to_attr='q_skus'
            ),
            Prefetch(
                'product_images',
                queryset=Image.objects.only('image_url').filter(store_id=store_pk),
                to_attr='q_images'
            )
    )\
        .filter(external_id__in=products_external_id, store_id=store_pk)
    return queryset, count
