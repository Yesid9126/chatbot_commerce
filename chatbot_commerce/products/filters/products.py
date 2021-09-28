from django_filters.rest_framework import FilterSet

from chatbot_commerce.products.models import Product, Skus

from django.db.models import Q, Prefetch

# from db_python import query_debugger


class ProductFilterSet(FilterSet):

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'brand__name': ['icontains'],
            'skus__name': ['icontains'],
            'skus__total_quantity': ['exact'],
        }

def products_skus(self):
    """
    Plane function of apply_filters of model Store.
    """

    # Apply filter products
    if self.store.apply_filter_enable_products and self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:
        skus = Skus.objects\
            .prefetch_related('price__fixed_prices')\
            .filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, ).distinct('pk')
        queryset = self.filter_queryset(
            Product.objects
            .select_related('department', 'category', 'sub_category', 'brand')
            .prefetch_related(
                Prefetch(
                    'skus',
                    queryset=skus
                )
            )
            .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True)
        ).distinct('external_id')

    elif self.store.apply_filter_enable_products or self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_products:
            if self.store.apply_filter_enable_skus:
                if self.store.apply_filter_image:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), total_quantity__gt=0, is_active=True, ).distinct('pk')
                    queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True)
                    ).distinct('pk')
                elif self.store.apply_filter_price:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, ).distinct('pk')
                    queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True)
                    ).distinct('external_id')
                else:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(total_quantity__gt=0, is_active=True, ).distinct('pk')
                    queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True)
                    ).distinct('external_id')
            elif self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, ).distinct('pk')
                    queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True)
                    ).distinct('external_id')
                else:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), ).distinct('pk')
                    queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True)
                    ).distinct('external_id')
            elif self.store.apply_filter_price:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(~Q(price=None), price__base_price__gt=0, ).distinct('pk')
                queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True)
                ).distinct('external_id')
            else:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter().distinct('pk')
                queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store, is_active=True)
                ).distinct('external_id')
        elif self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, ).distinct('pk')
                    queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store)
                    ).distinct('external_id')
                else:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), total_quantity__gt=0, is_active=True, ).distinct('pk')
                    queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store)
                    ).distinct('external_id')
            elif self.store.apply_filter_price:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, ).distinct('pk')
                queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store)
                ).distinct('external_id')
            else:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(total_quantity__gt=0, is_active=True, ).distinct('pk')
                queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store)
                ).distinct('external_id')
        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, ).distinct('pk')
                queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store)
                ).distinct('external_id')

            else:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(~Q(images=None), ).distinct('pk')
                queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store)
                ).distinct('external_id')

        else:
            skus = Skus.objects\
                .prefetch_related('price__fixed_prices')\
                .filter(~Q(price=None), price__base_price__gt=0, ).distinct('pk')
            queryset = self.filter_queryset(
                Product.objects
                .select_related('department', 'category', 'sub_category', 'brand')
                .prefetch_related(
                    Prefetch(
                        'skus',
                        queryset=skus
                    )
                )
                .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), store=self.store)
            ).distinct('external_id')

    else:

        queryset = self.filter_queryset(
            Product.objects
            .select_related('department', 'category', 'sub_category', 'brand')
            .prefetch_related(
                Prefetch(
                    'skus',
                    queryset=Skus.objects
                    .prefetch_related('price__fixed_prices')
                )
            )
            .filter(store=self.store)
        ).distinct('external_id')

    return queryset
