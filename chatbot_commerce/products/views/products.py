"""Product and skus views."""

# Django Rest Framework
from django.db.models import Prefetch
from chatbot_commerce.products.models.skus import Attribute, AttributeType, Skus
from chatbot_commerce.products.models.products import Brand
from rest_framework.generics import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

# Serializers
from chatbot_commerce.products.serializers import (ProductModelSerializer,
                                                   DepartmentTreeModelSerializer,
                                                   BrandsModelSerializer,
                                                   AttributeTypeModelSerializer)
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAdminUser

# Filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from chatbot_commerce.products.filters import ProductFilterSet
from chatbot_commerce.products.filters import products_skus

# Models
from chatbot_commerce.products.models import Product, Department
from chatbot_commerce.stores.models import Store

# Runtime
from db_python import query_debugger


class ProductViewset(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """Product viewset."""

    serializer_class = ProductModelSerializer
    lookup_field = 'pk'
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = ProductFilterSet
    search_fields = (
        'name', 'brand__name', 'keywords', 'category__name',
        'sub_category__name', 'department__name'
    )

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)

        swagger_params = ['attribute_type', 'attributes__value', 'sku_name']
        self.filter_data = {
            'attributes__attribute_type__name__icontains' if key == 'attribute_type' else
            'attributes__value__icontains' if key == 'attributes__value' else
            'name__icontains' if key == 'sku_name' else
            key+'__icontains': value for key, value in request.GET.items() if key in swagger_params
        }

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset

    @query_debugger
    def list(self, request, *args, **kwargs):
        """
        Return all products

        search = Put a keyword like name category or department to filter whith it
        example... search = jeans azul L
        """
        self.queryset = products_skus(self)
        serializer = self.get_serializer(self.paginate_queryset(self.queryset.order_by('-pk')), many=True)
        paginated_data = self.get_paginated_response(serializer.data).data
        return Response(data=paginated_data, status=HTTP_200_OK)

    @query_debugger
    def retrieve(self, request, *args, **kwargs):
        """
        Return a single product with his skus.

        Parameters.
        """
        try:
            obj = Product.objects\
                .select_related('department', 'category', 'sub_category', 'brand')\
                .prefetch_related(
                    Prefetch(
                        'skus', 
                        queryset=Skus.objects\
                            .prefetch_related('price__fixed_prices', 'attributes__attribute_type')\
                            .filter(**self.filter_data).distinct('pk')
                    ),
                )\
                .get(store=self.store, external_id=kwargs['pk'])
        except Exception as message:
            print(f'error. {message}')
            return Response({}, status=HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(obj).data, status=HTTP_200_OK)


class DepartmentsViewset(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):

    serializer_class = DepartmentTreeModelSerializer
    lookup_field = 'department_name'
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'categories__name', 'categories__subcategories__name')
    filter_fields = ('categories__name', 'categories__subcategories__name')

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Department.objects.filter(store=self.store).prefetch_related('categories__subcategories')
        return queryset

    # @query_debugger
    def list(self, request, *args, **kwargs):
        """
        Return all departments with tree category

        for search Put a keyword like name category or department to filter whith it
        example... search = Hombres
        """
        return super().list(request, *args, **kwargs)

    # @query_debugger
    def retrieve(self, request, *args, **kwargs):
        """
        Return a single department with tree category.

        Parameters.
        """
        obj = Department.objects.filter(store=self.store, name=kwargs['department_name']).prefetch_related('categories__subcategories').first()
        return Response(self.serializer_class(obj).data)


class BrandsViewset(mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = BrandsModelSerializer
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('name', 'title')

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        self.queryset = Brand.objects.filter(store=self.store).order_by()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset

    # @query_debugger
    def list(self, request, *args, **kwargs):
        """
        Return all brands of a store.

        Parameters.
        """
        queryset = self.filter_queryset(self.queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = [name for array in serializer.data for key, name in array.items() if key == 'name']
            paginated_data = self.get_paginated_response(data).data
            paginated_data['brands'] = paginated_data.pop('results')
            return Response(data=paginated_data, status=HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AttributesViewset(mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    serializer_class = AttributeTypeModelSerializer
    permission_classes = [HasAPIKey | IsAdminUser]
    filter_backends = (DjangoFilterBackend,)

    def dispatch(self, request, *args, **kwargs):
        slug_name = kwargs['store_slug_name']
        self.store = get_object_or_404(Store, slug_name=slug_name)
        self.attributes = Attribute.objects.filter(attribute_type__in=self.get_queryset())
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = AttributeType.objects.filter(store=self.store)
        return queryset

    def get_serializer_context(self):
        return self.attributes

    # @query_debugger
    def list(self, request, *args, **kwargs):
        """
        Return all attribute of a type.

        Parameters.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = {key: array for array in serializer.data for key, array in array.items()}
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
