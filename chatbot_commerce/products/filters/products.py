from django_filters.rest_framework import FilterSet
from django_filters import filters

from chatbot_commerce.products.models import Product, Skus

from django.db.models import Q, Prefetch

# from db_python import query_debugger


class ProductFilterSet(FilterSet):

    search__name = filters.CharFilter(field_name='skus__name')
    attributes = filters.CharFilter(field_name='skus__attributes__value')
    stock_quantity = filters.CharFilter(field_name='skus__total_quantity')
    category = filters.CharFilter(field_name='department__name')
    class Meta:
        model = Product
        fields = [
            'search__name', 'brand', 'category', 'attributes', 'stock_quantity'
        ]

def products_skus(self):
    """
    Plane function of apply_filters of model Store.
    """

    # Apply filter products
    if self.store.apply_filter_enable_products and self.store.apply_filter_enable_skus and self.store.apply_filter_image and self.store.apply_filter_price:
        skus = Skus.objects\
            .prefetch_related('price__fixed_prices')\
            .filter(~Q(images=None), ~Q(price=None), self.skus_filter_data[1] , price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.skus_filter_data[0]).distinct('pk')
        queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, is_active=True, **self.products_filter_data[0]).distinct('external_id')

    elif self.store.apply_filter_enable_products or self.store.apply_filter_enable_skus or self.store.apply_filter_image or self.store.apply_filter_price:
        if self.store.apply_filter_enable_products:
            if self.store.apply_filter_enable_skus:
                if self.store.apply_filter_image:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), self.skus_filter_data[1], total_quantity__gt=0, is_active=True, **self.skus_filter_data[0]).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, is_active=True, **self.products_filter_data[0]).distinct('pk')
                elif self.store.apply_filter_price:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(price=None), self.skus_filter_data[1], price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.skus_filter_data[0]).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, is_active=True, **self.products_filter_data[0]).distinct('external_id')
                else:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(self.skus_filter_data[1], total_quantity__gt=0, is_active=True, **self.skus_filter_data[0]).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, is_active=True, **self.products_filter_data[0]).distinct('external_id')
            elif self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), ~Q(price=None), self.skus_filter_data[1], price__base_price__gt=0, **self.skus_filter_data[0]).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, is_active=True, **self.products_filter_data[0]).distinct('external_id')
                else:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), self.skus_filter_data[1], **self.skus_filter_data[0]).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, is_active=True, **self.products_filter_data[0]).distinct('external_id')
            elif self.store.apply_filter_price:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(~Q(price=None), self.skus_filter_data[1], price__base_price__gt=0, **self.skus_filter_data[0]).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, is_active=True, **self.products_filter_data[0]).distinct('external_id')
            else:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(self.skus_filter_data[1], **self.skus_filter_data[0]).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, is_active=True, **self.products_filter_data[0]).distinct('external_id')
        elif self.store.apply_filter_enable_skus:
            if self.store.apply_filter_image:
                if self.store.apply_filter_price:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), ~Q(price=None), self.skus_filter_data[1], price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.skus_filter_data[0]).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, **self.products_filter_data[0]).distinct('external_id')
                else:
                    skus = Skus.objects\
                        .prefetch_related('price__fixed_prices')\
                        .filter(~Q(images=None), self.skus_filter_data[1], total_quantity__gt=0, is_active=True, **self.skus_filter_data[0]).distinct('pk')
                    queryset = Product.objects\
                        .select_related('department', 'category', 'sub_category', 'brand')\
                        .prefetch_related(
                            Prefetch(
                                'skus',
                                queryset=skus
                            )
                        )\
                        .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, **self.products_filter_data[0]).distinct('external_id')
            elif self.store.apply_filter_price:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(~Q(price=None), self.skus_filter_data[1], price__base_price__gt=0, total_quantity__gt=0, is_active=True, **self.skus_filter_data[0]).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, **self.products_filter_data[0]).distinct('external_id')
            else:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(self.skus_filter_data[1], total_quantity__gt=0, is_active=True, **self.skus_filter_data[0]).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, **self.products_filter_data[0]).distinct('external_id')
        elif self.store.apply_filter_image:
            if self.store.apply_filter_price:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(~Q(images=None), ~Q(price=None), self.skus_filter_data[1], price__base_price__gt=0, **self.skus_filter_data[0]).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, **self.products_filter_data[0]).distinct('external_id')

            else:
                skus = Skus.objects\
                    .prefetch_related('price__fixed_prices')\
                    .filter(~Q(images=None), self.skus_filter_data[1], **self.skus_filter_data[0]).distinct('pk')
                queryset = Product.objects\
                    .select_related('department', 'category', 'sub_category', 'brand')\
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=skus
                        )
                    )\
                    .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, **self.products_filter_data[0]).distinct('external_id')

        else:
            skus = Skus.objects\
                .prefetch_related('price__fixed_prices')\
                .filter(~Q(price=None), self.skus_filter_data[1], price__base_price__gt=0, **self.skus_filter_data[0]).distinct('pk')
            queryset = Product.objects\
                .select_related('department', 'category', 'sub_category', 'brand')\
                .prefetch_related(
                    Prefetch(
                        'skus',
                        queryset=skus
                    )
                )\
                .filter(Q(Q(skus__in=skus) & ~Q(skus=None)), self.products_filter_data[1], store=self.store, **self.products_filter_data[0]).distinct('external_id')

    else:

        queryset = Product.objects\
            .select_related('department', 'category', 'sub_category', 'brand')\
            .prefetch_related(
                Prefetch(
                    'skus',
                    queryset=Skus.objects.filter(self.skus_filter_data[1], **self.skus_filter_data[0]).distinct('pk')
                    .prefetch_related('price__fixed_prices')
                )
            )\
            .filter(self.products_filter_data[1], store=self.store, **self.products_filter_data[0]).distinct('external_id')

    return queryset

def filter_data_skus(self):
    skus_filter_data = [{}]
    total_quantity = self.data.get('stock_quantity')
    if total_quantity:
        skus_filter_data[0] |= {'total_quantity': total_quantity}
    name = self.data.get('search__name')
    if name:
        skus_filter_data[0] |= {'name__icontains': name}
    attributes = self.data.get('attributes')
    if attributes:
        attributes = attributes.split(',')
        if len(attributes) > 1:
            q = Q()
            for attribute in attributes:
                if attribute:
                    q |= Q(attributes__value__icontains=attribute)
            skus_filter_data.append(q)
        else:
            for attribute in attributes:
                if attribute:
                    skus_filter_data.append(Q(attributes__value__icontains=attribute))
    else:
        skus_filter_data.append(Q())
    return skus_filter_data

def filter_data_products(self):
    products_filter_data = [{}]
    name = self.data.get('search__name')
    if name:
        products_filter_data[0] |= {'name__icontains': name}
    brand = self.data.get('brand')
    if brand:
        products_filter_data[0] |= {'brand__name__icontains': brand}
    category = self.data.get('category')
    if category:
        q = Q(Q(department__name__icontains=category)|Q(category__name__icontains=category)|Q(sub_category__name__icontains=category))
        products_filter_data.append(q)
    else:
        products_filter_data.append(Q())
    return products_filter_data