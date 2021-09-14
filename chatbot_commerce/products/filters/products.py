from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

from chatbot_commerce.products.models import Product, Skus, Image, Price

from django.db.models import Q


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


def products_skus(self, filter_data):
    """
    Plane function of apply_filters of model Store.
    """

    # Apply filter products
    if self.store.apply_filter_enable_products:
        self.queryset = self.filter_queryset(Product.objects.filter(store__pk=self.store.pk, is_active=True).order_by())
    else:
        self.queryset = self.filter_queryset(Product.objects.filter(store__pk=self.store.pk).order_by())

    # Apply filter skus
    if self.store.apply_filter_image:
        sku_pks_images = Image.objects.filter(sku__product__store__pk=self.store.pk).order_by().values_list('sku__pk', flat=True)
    if self.store.apply_filter_price:
        sku_pks_prices = Price.objects.filter(~Q(base_price=None), sku__product__store__pk=self.store.pk, base_price__gt=0).order_by().values_list('sku__pk', flat=True)

    if self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:
        self.skus = Skus.objects.filter(
            Q(
                Q(pk__in=sku_pks_images) &
                Q(pk__in=sku_pks_prices)
            ),
            product__pk__in=self.queryset.values_list('pk', flat=True),
            is_active=True,
            total_quantity__gt=0,
            **filter_data).order_by()
    elif self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                self.skus = Skus.objects.filter(
                    Q(pk__in=sku_pks_images),
                    product__pk__in=self.queryset.values_list('pk', flat=True),
                    is_active=True,
                    total_quantity__gt=0,
                    **filter_data).order_by()
            elif self.store.apply_filter_price:
                self.skus = Skus.objects.filter(
                    Q(pk__in=sku_pks_prices),
                    product__pk__in=self.queryset.values_list('pk', flat=True),
                    is_active=True,
                    total_quantity__gt=0,
                    **filter_data).order_by()
            else:
                self.skus = Skus.objects.filter(
                    product__pk__in=self.queryset.values_list('pk', flat=True),
                    is_active=True,
                    total_quantity__gt=0,
                    **filter_data).order_by()
        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:
                self.skus = Skus.objects.filter(
                    Q(
                        Q(pk__in=sku_pks_images) &
                        Q(pk__in=sku_pks_prices)
                    ),
                    product__pk__in=self.queryset.values_list('pk', flat=True),
                    **filter_data).order_by()
            else:
                self.skus = Skus.objects.filter(
                    Q(pk__in=sku_pks_images),
                    product__pk__in=self.queryset.values_list('pk', flat=True),
                    **filter_data).order_by()
        else:
            self.skus = Skus.objects.filter(
                Q(pk__in=sku_pks_prices),
                product__pk__in=self.queryset.values_list('pk', flat=True),
                **filter_data).order_by()
    else:
        self.skus = Skus.objects.filter(product__pk__in=self.queryset.values_list('pk', flat=True), **filter_data).order_by()

    return self
