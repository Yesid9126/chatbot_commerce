from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

from chatbot_commerce.products.models import Product, Skus

from django.db.models import Q, Prefetch

# from db_python import query_debugger


class ProductFilterSet(FilterSet):
    attribute_type = filters.CharFilter(
        field_name='skus__attributes__attribute_type__name',
        lookup_expr='icontains',
        label='Type of attribute',
    )
    attributes__value = filters.CharFilter(
        field_name='skus__attributes__value',
        lookup_expr='icontains',
        label='Value of attribute',
    )
    sku_name = filters.CharFilter(
        field_name='skus__sku_name',
        lookup_expr='icontains',
        label='Sku name',
    )

    class Meta:
        model = Product
        fields = ['sku_name', 'attribute_type', 'attributes__value']


def products_skus(self):
    """
    Plane function of apply_filters of model Store.
    """

    # Apply filter products
    if self.store.apply_filter_enable_products and self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:

        skus = Skus.objects.filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.filter_data).distinct('pk')
        self.queryset = self.filter_queryset(
            Product.objects
            .select_related('department', 'category', 'sub_category', 'brand')
            .prefetch_related(Prefetch('skus', queryset=skus))
            .filter(store=self.store, skus__in=skus, is_active=True).distinct('pk')
        )

    elif self.store.apply_filter_enable_products or self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_products:
            if self.store.apply_filter_enable_skus:
                if self.store.apply_filter_image:
                    skus = Skus.objects.filter(~Q(images=None), total_quantity__gt=0, is_active=True, **self.filter_data).distinct('pk')
                    self.queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(Prefetch('skus', queryset=skus))
                        .filter(store=self.store, skus__in=skus, is_active=True).distinct('pk')
                    )
                elif self.store.apply_filter_price:
                    skus = Skus.objects.filter(~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.filter_data).distinct('pk')
                    self.queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(Prefetch('skus', queryset=skus))
                        .filter(store=self.store, skus__in=skus, is_active=True).distinct('pk')
                    )
                else:
                    skus = Skus.objects.filter(total_quantity__gt=0, is_active=True, **self.filter_data).distinct('pk')
                    self.queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(Prefetch('skus', queryset=skus))
                        .filter(store=self.store, skus__in=skus, is_active=True).distinct('pk')
                    )
            elif self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects.filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, **self.filter_data).distinct('pk')
                    self.queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(Prefetch('skus', queryset=skus))
                        .filter(store=self.store, skus__in=skus, is_active=True).distinct('pk')
                    )
                else:
                    skus = Skus.objects.filter(~Q(images=None), **self.filter_data).distinct('pk')
                    self.queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(Prefetch('skus', queryset=skus))
                        .filter(store=self.store, skus__in=skus, is_active=True).distinct('pk')
                    )
            elif self.store.apply_filter_price:
                skus = Skus.objects.filter(~Q(price=None), price__base_price__gt=0, **self.filter_data).distinct('pk')
                self.queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(Prefetch('skus', queryset=skus))
                    .filter(store=self.store, skus__in=skus, is_active=True).distinct('pk')
                )
            else:
                skus = Skus.objects.filter(**self.filter_data).distinct('pk')
                self.queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(Prefetch('skus', queryset=skus))
                    .filter(store=self.store, skus__in=skus, is_active=True).distinct('pk')
                )
        elif self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects.filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.filter_data).distinct('pk')
                    self.queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(Prefetch('skus', queryset=skus))
                        .filter(store=self.store, skus__in=skus).distinct('pk')
                    )
                else:
                    skus = Skus.objects.filter(~Q(images=None), total_quantity__gt=0, is_active=True, **self.filter_data).distinct('pk')
                    self.queryset = self.filter_queryset(
                        Product.objects
                        .select_related('department', 'category', 'sub_category', 'brand')
                        .prefetch_related(Prefetch('skus', queryset=skus))
                        .filter(store=self.store, skus__in=skus).distinct('pk')
                    )
            elif self.store.apply_filter_price:
                skus = Skus.objects.filter(~Q(price=None), price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.filter_data).distinct('pk')
                self.queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(Prefetch('skus', queryset=skus))
                    .filter(store=self.store, skus__in=skus).distinct('pk')
                )
            else:
                skus = Skus.objects.filter(total_quantity__gt=0, is_active=True, **self.filter_data).distinct('pk')
                self.queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(Prefetch('skus', queryset=skus))
                    .filter(store=self.store, skus__in=skus).distinct('pk')
                )
        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:

                skus = Skus.objects.filter(~Q(images=None), ~Q(price=None), price__base_price__gt=0, **self.filter_data).distinct('pk')
                self.queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(Prefetch('skus', queryset=skus))
                    .filter(store=self.store, skus__in=skus).distinct('pk')
                )

            else:

                skus = Skus.objects.filter(~Q(images=None), **self.filter_data).distinct('pk')
                self.queryset = self.filter_queryset(
                    Product.objects
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(Prefetch('skus', queryset=skus))
                    .filter(store=self.store, skus__in=skus).distinct('pk')
                )

        else:

            skus = Skus.objects.filter(~Q(price=None), price__base_price__gt=0, **self.filter_data).distinct('pk')
            self.queryset = self.filter_queryset(
                Product.objects
                .select_related('department', 'category', 'sub_category', 'brand')
                .prefetch_related(Prefetch('skus', queryset=skus))
                .filter(store=self.store, skus__in=skus).distinct('pk')
            )

    else:

        skus = Skus.objects.filter(**self.filter_data).distinct('pk')
        self.queryset = self.filter_queryset(
            Product.objects
            .select_related('department', 'category', 'sub_category', 'brand')
            .prefetch_related(Prefetch('skus', queryset=skus))
            .filter(store=self.store).distinct('pk')
        )

    self.skus = skus

    return self
