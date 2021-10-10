from django_filters.rest_framework import FilterSet
from django_filters import filters

from chatbot_commerce.stores.models import Product, Skus

from django.db.models import Q, Prefetch

# from db_python import query_debugger


class ProductFilterSet(FilterSet):

    # attributes = filters.CharFilter(field_name='name')
    stock_quantity = filters.CharFilter(field_name='name')
    offset = filters.CharFilter(field_name='name')
    limit = filters.CharFilter(field_name='name')

    class Meta:
        model = Product
        fields = [
            'offset',
            'limit',
            'search',
            #  'attributes',
            'stock_quantity',
        ]


def products_skus(self, store_pk):
    """
    Plane function of apply_filters of model Store.
    """

    # Apply filter products
    if self.store.apply_filter_enable_products and self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:
        print('1')
        skus_pk = Skus.objects\
            .filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True)\
            .values_list('pk', flat=True).distinct('pk')
        print('2')
        products_pk = Product.objects.filter(store_id=store_pk, skus__pk__in=skus_pk, is_active=True).values_list('pk', flat=True).distinct('pk')[self.offset:self.limit]
        print('3')
        queryset = Product.objects\
            .select_related('department', 'category', 'sub_category', 'brand')\
            .prefetch_related(
                Prefetch(
                    'skus',
                    queryset=Skus.objects.filter(pk__in=skus_pk, product_id__in=products_pk)
                )
            )\
            .filter(pk__in=products_pk).order_by('-external_id')
        print('4')

    elif self.store.apply_filter_enable_products or self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_products:
            if self.store.apply_filter_enable_skus:
                if self.store.apply_filter_image:
                    skus_pk = Skus.objects\
                        .filter(~Q(images=None), **self.skus_filter_data, total_quantity__gt=0, is_active=True)\
                        .values_list('pk', flat=True).distinct('pk')
                elif self.store.apply_filter_price:
                    skus_pk = Skus.objects\
                        .filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True)\
                        .values_list('pk', flat=True).distinct('pk')
                else:
                    skus_pk = Skus.objects\
                        .filter(**self.skus_filter_data, total_quantity__gt=0, is_active=True)\
                        .values_list('pk', flat=True).distinct('pk')
            elif self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus_pk = Skus.objects\
                        .filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0)\
                        .values_list('pk', flat=True).distinct('pk')
                else:
                    skus_pk = Skus.objects\
                        .filter(~Q(images=None), **self.skus_filter_data)\
                        .values_list('pk', flat=True).distinct('pk')
            elif self.store.apply_filter_price:
                skus_pk = Skus.objects\
                    .filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0)\
                    .values_list('pk', flat=True).distinct('pk')
            else:
                skus_pk = Skus.objects\
                    .filter(**self.skus_filter_data)\
                    .values_list('pk', flat=True).distinct('pk')
            products_pk = Product.objects.filter(skus__pk__in=skus_pk, store_id=store_pk, is_active=True).values_list('pk', flat=True).distinct('pk')[self.offset:self.limit]
            queryset = Product.objects\
                .select_related('department', 'category', 'sub_category', 'brand')\
                .prefetch_related(
                    Prefetch(
                        'skus',
                        queryset=Skus.objects.filter(pk__in=skus_pk, product_id__in=products_pk)
                    )
                )\
                .filter(pk__in=products_pk).order_by('-external_id')
        elif self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus_pk = Skus.objects\
                        .filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True)\
                        .values_list('pk', flat=True).distinct('pk')
                else:
                    skus_pk = Skus.objects\
                        .filter(~Q(images=None), **self.skus_filter_data, total_quantity__gt=0, is_active=True)\
                        .values_list('pk', flat=True).distinct('pk')
            elif self.store.apply_filter_price:
                skus_pk = Skus.objects\
                    .filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True)\
                    .values_list('pk', flat=True).distinct('pk')
            else:
                skus_pk = Skus.objects\
                    .filter(**self.skus_filter_data, total_quantity__gt=0, is_active=True)\
                    .values_list('pk', flat=True).distinct('pk')
            products_pk = Product.objects.filter(skus__pk__in=skus_pk, store_id=store_pk).values_list('pk', flat=True).distinct('pk')[self.offset:self.limit]
            queryset = Product.objects\
                .select_related('department', 'category', 'sub_category', 'brand')\
                .prefetch_related(
                    Prefetch(
                        'skus',
                        queryset=Skus.objects.filter(pk__in=skus_pk, product_id__in=products_pk)
                    )
                )\
                .filter(pk__in=products_pk).order_by('-external_id')
        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:
                skus_pk = Skus.objects\
                    .filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0)\
                    .values_list('pk', flat=True).distinct('pk')
            else:
                skus_pk = Skus.objects\
                    .filter(~Q(images=None), **self.skus_filter_data)\
                    .values_list('pk', flat=True).distinct('pk')
            products_pk = Product.objects.filter(skus__pk__in=skus_pk, store_id=store_pk).values_list('pk', flat=True).distinct('pk')[self.offset:self.limit]
            queryset = Product.objects\
                .select_related('department', 'category', 'sub_category', 'brand')\
                .prefetch_related(
                    Prefetch(
                        'skus',
                        queryset=Skus.objects.filter(pk__in=skus_pk, product_id__in=products_pk)
                    )
                )\
                .filter(pk__in=products_pk).order_by('-external_id')

        else:
            skus_pk = Skus.objects\
                .filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0)\
                .values_list('pk', flat=True).distinct('pk')
            products_pk = Product.objects.filter(skus__pk__in=skus_pk, store_id=store_pk).values_list('pk', flat=True).distinct('pk')[self.offset:self.limit]
            queryset = Product.objects\
                .select_related('department', 'category', 'sub_category', 'brand')\
                .prefetch_related(
                    Prefetch(
                        'skus',
                        queryset=Skus.objects.filter(pk__in=skus_pk, product_id__in=products_pk)
                    )
                )\
                .filter(pk__in=products_pk).order_by('-external_id')

    else:
        skus_pk = Skus.objects\
            .filter(**self.skus_filter_data)\
            .values_list('pk', flat=True).distinct('pk')
        products_pk = Product.objects.filter(skus__pk__in=skus_pk, store_id=store_pk).values_list('pk', flat=True).distinct('pk')[self.offset:self.limit]
        queryset = Product.objects\
            .select_related('department', 'category', 'sub_category', 'brand')\
            .prefetch_related(
                Prefetch(
                    'skus',
                    queryset=Skus.objects.filter(pk__in=skus_pk, product_id__in=products_pk)
                )
            )\
            .filter(pk__in=products_pk).order_by('-external_id')

    return queryset
