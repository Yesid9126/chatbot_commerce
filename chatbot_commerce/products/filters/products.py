from django_filters.rest_framework import FilterSet
from django_filters import filters

from chatbot_commerce.products.models import Product, Skus

from django.db.models import Q, Prefetch

# from db_python import query_debugger


class ProductFilterSet(FilterSet):

    attributes = filters.CharFilter(field_name='name')
    stock_quantity = filters.CharFilter(field_name='skus__total_quantity')

    class Meta:
        model = Product
        fields = [
            'search', 'attributes', 'stock_quantity'
        ]


def products_skus(self):
    """
    Plane function of apply_filters of model Store.
    """

    # Apply filter products
    if self.store.apply_filter_enable_products and self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:
        skus = Skus.objects\
        .filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.skus_filter_data).distinct('pk')
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
                    .filter(~Q(images=None), total_quantity__gt=0, is_active=True, **self.skus_filter_data).distinct('pk')
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
                    .filter(~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.skus_filter_data).distinct('pk')
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
                    .filter(total_quantity__gt=0, is_active=True, **self.skus_filter_data).distinct('pk')
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
                    .filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, **self.skus_filter_data).distinct('pk')
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
                .filter(~Q(price=None), price__base_price__gt=0, **self.skus_filter_data).distinct('pk')
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
                    .filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.skus_filter_data).distinct('pk')
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
                    .filter(~Q(images=None), total_quantity__gt=0, is_active=True, **self.skus_filter_data).distinct('pk')
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
                .filter(~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.skus_filter_data).distinct('pk')
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
                .filter(total_quantity__gt=0, is_active=True, **self.skus_filter_data).distinct('pk')
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
                .filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, **self.skus_filter_data).distinct('pk')
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
            .filter(~Q(price=None), price__base_price__gt=0, **self.skus_filter_data).distinct('pk')
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
    skus_filter_data = {}
    total_quantity = self.data.get('stock_quantity')
    if total_quantity:
        skus_filter_data |= {'total_quantity': total_quantity}
    search = self.data.get('search')
    if search:
        skus_filter_data |= {'search__search': search}
    attributes = self.data.get('attributes')
    if attributes:
        attributes = attributes.replace('-', ' ')
        skus_filter_data |= {'search_attributes__search': attributes}

    return skus_filter_data
