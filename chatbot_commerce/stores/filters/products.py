# Django
from django_filters.rest_framework import FilterSet
from django_filters import filters

# Models
from chatbot_commerce.stores.models import Product, Sku, Image
from django.db.models import Q, Prefetch

# Utils
from numpy.random import shuffle
from django.core.cache import cache
# from db_python import query_debugger


class ProductFilterSet(FilterSet):

    # attributes = filters.CharFilter(field_name='name')
    budget = filters.NumberFilter(field_name='name', lookup_expr='lte')
    stock_quantity = filters.NumberFilter(field_name='name', lookup_expr='gte')
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
        sku_q = [~Q(images=None), ~Q(sku_price=None), ~Q(sku_price=0), ~Q(total_quantity=0)]
        sku_d = self.skus_filter_data | {'is_active': True, 'product__store': store_pk}
        product_d['is_active'] = True

    elif self.store.apply_filter_enable_products or self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_products:
            if self.store.apply_filter_enable_skus:
                if self.store.apply_filter_image:
                    sku_q = [~Q(images=None), ~Q(total_quantity=0)]
                    sku_d = self.skus_filter_data | {'is_active': True, 'product__store': store_pk}
                elif self.store.apply_filter_price:
                    sku_q = [~Q(sku_price=None), Q(sku_price=0), ~Q(total_quantity=0)]
                    sku_d = self.skus_filter_data | {'is_active': True, 'product__store': store_pk}
                else:
                    sku_q = [Q(sku_price=0), ~Q(total_quantity=0)]
                    sku_d = self.skus_filter_data | {'is_active': True, 'product__store': store_pk}
            elif self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    sku_q = [~Q(images=None), ~Q(sku_price=None), Q(sku_price=0)]
                    sku_d = self.skus_filter_data | {'product__store': store_pk}
                else:
                    sku_q = [~Q(images=None)]
                    sku_d = self.skus_filter_data | {'product__store': store_pk}
            elif self.store.apply_filter_price:
                sku_q = [~Q(sku_price=None), Q(sku_price=0)]
                sku_d = self.skus_filter_data | {'product__store': store_pk}
            else:
                sku_q = list()
                sku_d = self.skus_filter_data | {'product__store': store_pk}
            product_d['is_active'] = True

        elif self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    sku_q = [~Q(images=None), ~Q(sku_price=None), Q(sku_price=0), ~Q(total_quantity=0)]
                    sku_d = self.skus_filter_data | {'is_active': True, 'product__store': store_pk}
                else:
                    sku_q = [~Q(images=None), ~Q(total_quantity=0)]
                    sku_d = self.skus_filter_data | {'is_active': True, 'product__store': store_pk}
            elif self.store.apply_filter_price:
                sku_q = [~Q(sku_price=None), Q(sku_price=0), ~Q(total_quantity=0)]
                sku_d = self.skus_filter_data | {'is_active': True, 'product__store': store_pk}
            else:
                sku_q = [~Q(total_quantity=0)]
                sku_d = self.skus_filter_data | {'is_active': True, 'product__store': store_pk}

        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:
                sku_q = [~Q(images=None), ~Q(sku_price=None), Q(sku_price=0)]
                sku_d = self.skus_filter_data | {'product__store': store_pk}
            else:
                sku_q = [~Q(images=None)]
                sku_d = self.skus_filter_data | {'product__store': store_pk}

        else:
            sku_q = [~Q(sku_price=None), Q(sku_price=0)]
            sku_d = self.skus_filter_data | {'product__store': store_pk}

    else:
        sku_q = list()
        sku_d = self.skus_filter_data | {'product__store': store_pk}

    data = cache.get(key=self.cache_key)
    if data:
        count = data.get('count')
        skus_pk = data.get('skus_pk')
        products_pk = data.get('products_pk')
        shuffle(products_pk)

    else:
        product_is_active = product_d.get('is_active')
        if product_is_active:
            skus_pk = set(Sku.objects
                          .filter(*sku_q, **sku_d, product__is_active=True)
                          .values_list('pk', flat=True))
            products_pk = list(set(Sku.objects
                                   .filter(*sku_q, **sku_d, product__is_active=True)
                                   .values_list('product', flat=True)))
        else:
            skus_pk = set(Sku.objects
                          .filter(*sku_q, **sku_d)
                          .values_list('pk', flat=True))
            products_pk = list(set(Sku.objects
                                   .filter(*sku_q, **sku_d)
                                   .values_list('product', flat=True)))
        # products_external_id = sorted(products_external_id)
        count = len(products_pk)
        # shuffle(products_pk)
        # products_external_id.reverse()
        if count:
            data = {
                'products_pk': products_pk,
                'skus_pk': skus_pk,
                'count': count
            }
            cache.set(key=self.cache_key, value=data, timeout=60 * 60)
    products_pk = products_pk[self.offset:self.limit]
    queryset = Product.objects.only('external_id', 'name', 'keywords', 'department', 'category', 'sub_category', 'brand')\
        .select_related('department', 'category', 'sub_category', 'brand')\
        .prefetch_related(
            Prefetch(
                'skus',
                queryset=Sku.objects.only('serializer_data', 'product').filter(pk__in=skus_pk, product__pk__in=products_pk),
                to_attr='q_skus'
            ),
            Prefetch(
                'product_images',
                queryset=Image.objects.only('image_url').filter(store_id=store_pk),
                to_attr='q_images'
            )
    )\
        .filter(pk__in=products_pk)
    return queryset, count
