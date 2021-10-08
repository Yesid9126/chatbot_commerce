from django_filters.rest_framework import FilterSet
from django_filters import filters

from chatbot_commerce.stores.models import Product, Skus

from django.db.models import Q, Prefetch

# from db_python import query_debugger


class ProductFilterSet(FilterSet):

    # attributes = filters.CharFilter(field_name='name')
    stock_quantity = filters.CharFilter(field_name='skus__total_quantity')

    class Meta:
        model = Product
        fields = [
            'search',
            #  'attributes',
            'stock_quantity'
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
            .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')

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
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')
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
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')
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
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')
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
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')
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
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')
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
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')
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
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True).distinct('external_id').order_by('-external_id')
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
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')
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
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')
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
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')
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
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')
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
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')

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
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')

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
                .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store).distinct('external_id').order_by('-external_id')

    else:

        queryset = Product.objects\
            .select_related('department', 'category', 'sub_category', 'brand')\
            .prefetch_related(
                Prefetch(
                    'skus',
                    queryset=Skus.objects.filter(**self.skus_filter_data)
                )
            )\
            .filter(store=self.store).order_by('-external_id')

    return queryset


def filter_data_skus(self):
    return {
        # 'search_attributes' if key == 'attributes' else\
        'search_vector' if key == 'search' else\
        'total_quantity': value for key, value in self.request.GET.items() if key in ('stock_quantity', 'search',)
    }
