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


def products_skus(self):
    """
    Plane function of apply_filters of model Store.
    """

    # Apply filter products
    if self.store.apply_filter_enable_products and self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:
        skus = Skus.objects\
            .filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True).distinct('pk')
        queryset = Product.objects\
            .select_related('department', 'category', 'sub_category', 'brand')\
            .prefetch_related(
                Prefetch(
                    'skus',
                    queryset=skus
                )
            )\
            .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')[self.offset:self.limit]

    elif self.store.apply_filter_enable_products or self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_products:
            if self.store.apply_filter_enable_skus:
                if self.store.apply_filter_image:
                    skus = Skus.objects\
                        .filter(~Q(images=None), **self.skus_filter_data, total_quantity__gt=0, is_active=True).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
                elif self.store.apply_filter_price:
                    skus = Skus.objects\
                        .filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
                else:
                    skus = Skus.objects\
                        .filter(**self.skus_filter_data, total_quantity__gt=0, is_active=True).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
            elif self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects\
                        .filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
                else:
                    skus = Skus.objects\
                        .filter(~Q(images=None), **self.skus_filter_data).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
            elif self.store.apply_filter_price:
                skus = Skus.objects\
                    .filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
            else:
                skus = Skus.objects\
                    .filter(**self.skus_filter_data)
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
        elif self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects\
                        .filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
                else:
                    skus = Skus.objects\
                        .filter(~Q(images=None), **self.skus_filter_data, total_quantity__gt=0, is_active=True).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
            elif self.store.apply_filter_price:
                skus = Skus.objects\
                    .filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
            else:
                skus = Skus.objects\
                    .filter(**self.skus_filter_data, total_quantity__gt=0, is_active=True).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')[self.offset:self.limit]
        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:
                skus = Skus.objects\
                    .filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')[self.offset:self.limit]

            else:
                skus = Skus.objects\
                    .filter(~Q(images=None), **self.skus_filter_data).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')[self.offset:self.limit]

        else:
            skus = Skus.objects\
                .filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0).distinct('pk')
            queryset = Product.objects\
                .select_related('department', 'category', 'sub_category', 'brand')\
                .prefetch_related(
                    Prefetch(
                        'skus',
                        queryset=skus
                    )
                )\
                .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')[self.offset:self.limit]

    else:

        queryset = Product.objects\
            .select_related('department', 'category', 'sub_category', 'brand')\
            .prefetch_related(
                Prefetch(
                    'skus',
                    queryset=Skus.objects.filter(**self.skus_filter_data)
                )
            )\
            .filter(store=self.store).order_by('-external_id')[self.offset:self.limit]

    return queryset

def count_products(self):
    """
    Plane function of apply_filters of model Store.
    """

    # Apply filter products
    if self.store.apply_filter_enable_products and self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:
        skus = Skus.objects.filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True).values_list('pk', flat=True)
        count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('pk').values_list('pk', flat=True))

    elif self.store.apply_filter_enable_products or self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_products:
            if self.store.apply_filter_enable_skus:
                if self.store.apply_filter_image:
                    skus = Skus.objects.filter(~Q(images=None), **self.skus_filter_data, total_quantity__gt=0, is_active=True).values_list('pk', flat=True)
                    count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('pk').values_list('pk', flat=True))
                elif self.store.apply_filter_price:
                    skus = Skus.objects.filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True).values_list('pk', flat=True)
                    count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('pk').values_list('pk', flat=True))
                else:
                    skus = Skus.objects.filter(**self.skus_filter_data, total_quantity__gt=0, is_active=True).values_list('pk', flat=True)
                    count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('pk').values_list('pk', flat=True))
            elif self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects.filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0).values_list('pk', flat=True)
                    count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('pk').values_list('pk', flat=True))
                else:
                    skus = Skus.objects.filter(~Q(images=None), **self.skus_filter_data).values_list('pk', flat=True)
                    count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('pk').values_list('pk', flat=True))
            elif self.store.apply_filter_price:
                skus = Skus.objects.filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0).values_list('pk', flat=True)
                count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('pk').values_list('pk', flat=True))
            else:
                skus = Skus.objects.filter(**self.skus_filter_data).values_list('pk', flat=True)
                count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('pk').values_list('pk', flat=True))
        elif self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects.filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True).values_list('pk', flat=True)
                    count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('pk').values_list('pk', flat=True))
                else:
                    skus = Skus.objects.filter(~Q(images=None), **self.skus_filter_data, total_quantity__gt=0, is_active=True).values_list('pk', flat=True)
                    count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('pk').values_list('pk', flat=True))
            elif self.store.apply_filter_price:
                skus = Skus.objects.filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0, total_quantity__gt=0, is_active=True).values_list('pk', flat=True)
                count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('pk').values_list('pk', flat=True))
            else:
                skus = Skus.objects.filter(**self.skus_filter_data, total_quantity__gt=0, is_active=True).values_list('pk', flat=True)
                count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('pk').values_list('pk', flat=True))
        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:
                skus = Skus.objects.filter(~Q(images=None), ~Q(price=None), **self.skus_filter_data, price__base_price__gt=0).values_list('pk', flat=True)
                count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('pk').values_list('pk', flat=True))

            else:
                skus = Skus.objects.filter(~Q(images=None), **self.skus_filter_data).values_list('pk', flat=True)
                count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('pk').values_list('pk', flat=True))

        else:
            skus = Skus.objects.filter(~Q(price=None), **self.skus_filter_data, price__base_price__gt=0).values_list('pk', flat=True)
            count = len(Product.objects.filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('pk').values_list('pk', flat=True))

    else:
        count = len(Product.objects.filter(store=self.store).values_list('pk', flat=True))

    return count
