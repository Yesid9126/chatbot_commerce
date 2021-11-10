"""Product and skus views."""

# Django
from django.db.models import Prefetch
from django.http import HttpResponseBadRequest

# Django Rest Framework
from rest_framework import viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

# Serializers
from chatbot_commerce.stores.serializers import (ProductModelSerializer,
                                                 DepartmentTreeModelSerializer,
                                                 AttributeTypeModelSerializer)
from chatbot_commerce.stores.permissions import HasStoreAPIKey
from rest_framework.permissions import IsAdminUser

# Filters
from rest_framework.filters import SearchFilter
from chatbot_commerce.stores.filters import ProductFilterSet, products_skus

# Models
from chatbot_commerce.stores.models import (
    Store, Brand, Department, Category, Subcategory,
    Product,
    Skus, AttributeType, Image,
    # SearchAnalizer,
)

# Paginator
from chatbot_commerce.utils.paginators import page_url

# Cache
from django.core.cache import cache

# Runtime
from db_python import query_debugger
# from chatbot_commerce.utils.search_analizer import search_analizer_manager


class ProductViewset(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """Product viewset."""

    serializer_class = ProductModelSerializer
    lookup_field = 'pk'
    permission_classes = [HasStoreAPIKey | IsAdminUser]
    filter_class = ProductFilterSet

    # @query_debugger
    def dispatch(self, request, *args, **kwargs):

        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store.objects.select_related('store_type'), name=slug_name)
        # self.search = self.request.GET.get('search')
        self.skus_filter_data = {
            # 'search_attributes' if key == 'attributes' else\
            'search_vector' if key == 'search' else\
            'total_quantity' if key == 'stock_quantity' else\
            key: value for key, value in self.request.GET.items() if key in ('stock_quantity', 'search', 'offset', 'limit', 'page')
        }

        if 'limit' in self.skus_filter_data:
            limit = int(self.skus_filter_data.pop('limit'))
        else:
            limit = 50

        if 'offset' in self.skus_filter_data:
            q_offset = int(self.skus_filter_data.pop('offset'))
        else:
            q_offset = 0

        self.page = 1
        self.page_error = Exception('Page not found try with a number int() with base 10: page > 0')
        if 'page' in self.skus_filter_data:
            try:
                page = int(self.skus_filter_data.pop('page'))
                assert(page >= 1)
                if page > 1:
                    self.page = page
            except (AssertionError, TypeError, ValueError):
                return HttpResponseBadRequest(self.page_error)
        self.offset = q_offset + limit*(self.page - 1)
        self.limit = self.offset + limit
        self.current_size_position = self.limit - q_offset

        return super().dispatch(request, *args, **kwargs)

    @query_debugger
    def list(self, request, *args, **kwargs):
        """
        Return all products

        search = Put a keyword like name category or department to filter whith it
        example... search = jeans azul L
        """

        base_url = self.request.build_absolute_uri()
        cache_key = base_url.replace('?', '').replace('&', '').replace('/', '').lower()
        paginated_data = cache.get(key=cache_key)
        if paginated_data:

            # if self.search:
            #     obj, _ = SearchAnalizer.objects.get_or_create(store=self.store, search=self.search, defaults={'date_count': {'count': 0}})
            #     search_analizer_manager(self=self, obj=obj)

            return Response(data=paginated_data, status=HTTP_200_OK)

        store_pk = self.store.pk
        query, count = products_skus(self, store_pk=store_pk)
        differ = self.limit - count
        page_size = self.limit - self.offset
        if differ > -1:
            page_size = page_size - differ

        data = self.get_serializer(query, many=True, read_only=True).data
        try:
            assert(data != [])
        except AssertionError:
            return HttpResponseBadRequest(self.page_error)

        next_link, previous_link = page_url(page=self.page, base_url=base_url, differ=differ)
        count -= self.limit - self.current_size_position
        paginated_data = {
            'count': count,
            'page_size': page_size,
            'next_link': next_link,
            'previous_link': previous_link,
            'results': data
        }
        cache.set(key=cache_key, value=paginated_data, timeout=30)
        # if self.search:
        #     obj, _ = SearchAnalizer.objects.get_or_create(store=self.store, search=self.search, defaults={'date_count': {'count': 0}})
        #     search_analizer_manager(self=self, obj=obj)
        return Response(data=paginated_data, status=HTTP_200_OK)

    @query_debugger
    def retrieve(self, request, *args, **kwargs):
        """
        Return a single product with his skus.

        Parameters.
        """

        try:
            return Response(
                self.get_serializer(
                    Product.objects
                    .only('external_id', 'name', 'keywords', 'department', 'category', 'sub_category', 'brand')
                    .select_related('department', 'category', 'sub_category', 'brand')
                    .prefetch_related(
                        Prefetch(
                            'skus',
                            queryset=Skus.objects
                            .only('serializer_data', 'product')
                            .filter(**self.skus_filter_data),
                            to_attr='q_skus'
                        ),
                        Prefetch(
                            'product_images',
                            queryset=Image.objects.only('image_url').filter(store=self.store),
                            to_attr='q_images'
                        )
                    )
                    .get(store=self.store, external_id=kwargs['pk']),
                    read_only=True
                ).data,
                status=HTTP_200_OK
            )
        except Exception as message:
            print(f'error. {message}')
            return Response({}, status=HTTP_404_NOT_FOUND)


class DepartmentsViewset(mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    serializer_class = DepartmentTreeModelSerializer
    permission_classes = [HasStoreAPIKey | IsAdminUser]
    filter_backends = (SearchFilter,)

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store.objects.select_related('store_type'), name=slug_name)
        return super().dispatch(request, *args, **kwargs)

    # @query_debugger
    def list(self, request, *args, **kwargs):
        """
        Return all departments with tree category

        for search Put a keyword like name category or department to filter whith it
        example... search = Hombres
        """
        base_url = self.request.build_absolute_uri()
        cache_key = base_url.replace('?', '').replace('&', '').replace('/', '').lower()
        data = cache.get(key=cache_key)
        if data:
            return Response(data=data, status=HTTP_200_OK)
        search = request.GET.get('search')
        if search:
            search = {'name__iexact': search}
            if Department.objects.filter(**search, stores=self.store).exists():

                queryset = Department.objects\
                    .only('name',)\
                    .filter(**search, stores=self.store)\
                    .prefetch_related(
                        Prefetch(
                            'categories',
                            queryset=Category.objects
                            .only('name', 'department',)
                            .filter(store=self.store)
                            .prefetch_related(
                                Prefetch(
                                    'subcategories',
                                    queryset=Subcategory.objects.only('name', 'category',).filter(category__store=self.store),
                                    to_attr='q_subcategories'
                                )
                            ),
                            to_attr='q_categories'
                        )
                    )

                data = [
                    {
                        'name': deparment.name,
                        'categories': [
                            {
                                'name': category.name,
                                'subcategories': [
                                    {'name': subcategory.name}
                                    for subcategory in category.q_subcategories
                                ]
                            }
                            for category in deparment.q_categories
                        ]

                    }
                    for deparment in queryset
                ]

            elif Category.objects.filter(**search, store=self.store).exists():

                queryset = Category.objects\
                    .only('name', 'department',)\
                    .select_related('department')\
                    .prefetch_related(
                        Prefetch(
                            'subcategories',
                            queryset=Subcategory.objects.only('name', 'category').filter(category__store=self.store),
                            to_attr='q_subcategories'
                        )
                    )\
                    .filter(store=self.store, **search)

                data = [
                    {
                        'name': category.department.name,
                        'categories': [
                            {
                                'name': category.name,
                                'subcategories': [
                                    {'name': subcategory.name}
                                    for subcategory in category.q_subcategories
                                ]
                            }
                        ]
                    }
                    for category in queryset
                ]

            elif Subcategory.objects.filter(**search, category__store=self.store).exists():

                queryset = Subcategory.objects\
                    .only('name', 'category',)\
                    .select_related('category__department')\
                    .filter(category__store=self.store, **search)

                data = [
                    {
                        'name': subcategory.category.department.name,
                        'categories': [
                            {
                                'name': subcategory.category.name,
                                'subcategories': [
                                    {
                                        'name': subcategory.name,
                                    }
                                ]
                            }
                        ]
                    }
                    for subcategory in queryset
                ]

            else:
                return Response(data=[], status=HTTP_404_NOT_FOUND)

            cache.set(key=cache_key, value=data, timeout=360)
            return Response(data=data, status=HTTP_200_OK)

        queryset = Department.objects\
            .only('name',)\
            .filter(stores=self.store)\
            .prefetch_related(
                Prefetch(
                    'categories',
                    queryset=Category.objects
                    .only('name', 'department',)
                    .filter(store=self.store)
                    .prefetch_related(
                        Prefetch(
                            'subcategories',
                            queryset=Subcategory.objects.only('name', 'category',).filter(category__store=self.store),
                            to_attr='q_subcategories'
                        )
                    ),
                    to_attr='q_categories'
                )
            )

        data = [
            {
                'name': deparment.name,
                'categories': [
                    {
                        'name': category.name,
                        'subcategories': [
                            {'name': subcategory.name}
                            for subcategory in category.q_subcategories
                        ]
                    }
                    for category in deparment.q_categories
                ]

            }
            for deparment in queryset
        ]

        cache.set(key=cache_key, value=data, timeout=360)
        return Response(
            data=data,
            status=HTTP_200_OK
        )


class BrandsViewset(mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    permission_classes = [HasStoreAPIKey | IsAdminUser]

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store.objects.select_related('store_type'), name=slug_name)
        self.queryset = Brand.objects.filter(stores=self.store)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset

    # @query_debugger
    def list(self, request, *args, **kwargs):
        """
        Return all brands of a store.

        Parameters.
        """
        return Response(
            {
                'count': len(self.queryset.values_list('name', flat=True)),
                'brands': self.queryset.values_list('name', flat=True),
            }
        )


class AttributesViewset(mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    serializer_class = AttributeTypeModelSerializer
    permission_classes = [HasStoreAPIKey | IsAdminUser]

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store.objects.select_related('store_type'), name=slug_name)
        return super().dispatch(request, *args, **kwargs)

    # @query_debugger
    def list(self, request, *args, **kwargs):
        """
        Return all attribute of a type.

        Parameters.
        """
        base_url = self.request.build_absolute_uri()
        cache_key = base_url.replace('/', '').lower().split('?')[0]
        data = cache.get(key=cache_key)
        if data:
            return Response(data=data, status=HTTP_200_OK)
        queryset = AttributeType.objects\
            .filter(store=self.store)\
            .prefetch_related(Prefetch('attributes', to_attr='q_attributes'))
        data = {attribute_type.name: sorted({attribute.value for attribute in attribute_type.q_attributes}) for attribute_type in queryset}
        cache.set(key=cache_key, value=data, timeout=360)
        return Response(data)
