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
    user = filters.CharFilter(field_name='name')

    class Meta:
        model = Product
        fields = [
            'offset',
            'limit',
            'search',
            'page',
            'user',
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

    data_cache = cache.get(key=self.cache_key)
    if data_cache:
        count = data_cache.get('count')
        skus_pk = data_cache.get('skus_pk')
        products_pk = data_cache.get('products_pk')
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
            shuffle(products_pk)
            data = {
                'products_pk': products_pk,
                'skus_pk': skus_pk,
                'count': count
            }
            cache.set(key=self.cache_key, value=data, timeout=60 * 60)

    if self.user:
        user_products_pk = cache.get(key=self.user_cache_key)
        if not user_products_pk:
            shuffle(products_pk)
            cache.set(key=self.user_cache_key, value=products_pk, timeout=60 * 15)
        else:
            products_pk = user_products_pk
    page_products_pk = products_pk[self.offset:self.limit]

    queryset = Product.objects.only('external_id', 'name', 'keywords', 'department', 'category', 'sub_category', 'brand')\
        .select_related('department', 'category', 'sub_category', 'brand')\
        .prefetch_related(
            Prefetch(
                'skus',
                queryset=Sku.objects.only(
                    'product',
                    'external_id',
                    'sellers_id',
                    'name',
                    'total_quantity',
                    'images_url',
                    'price_data',
                    'attributes_data',
                    'is_active'
                ).filter(pk__in=skus_pk, product__pk__in=page_products_pk),
                to_attr='q_skus'
            ),
            Prefetch(
                'product_images',
                queryset=Image.objects.only('image_url').filter(product__store=store_pk),
                to_attr='q_images'
            )
    )\
        .filter(pk__in=page_products_pk)
    return queryset, count
